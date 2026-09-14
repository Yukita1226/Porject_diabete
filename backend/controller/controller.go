package controller

import (
	"bufio"
	"encoding/json"
	"fmt"
	"bytes"
	"io"
	"net/http"
	"os"
	"os/exec"
	"sync"

	"github.com/gin-gonic/gin"

	"pk/backend/entity"
)

type Bridge struct {
	mu  sync.Mutex
	cmd *exec.Cmd
	in  io.WriteCloser
	out *bufio.Reader
	seq int
}

var bridge *Bridge

func Startbridge(dir, script string) error {
	c := exec.Command(`C:\Users\tham\AppData\Local\Programs\Python\Python312\python.exe`, "-u", script)  // fix this
	c.Dir = dir
	c.Stderr = os.Stderr

	in, err := c.StdinPipe()
	if err != nil {
		return err
	}
	out, err := c.StdoutPipe()
	if err != nil {
		return err
	}
	if err := c.Start(); err != nil {
		return err
	}

	bridge = &Bridge{cmd: c, in: in, out: bufio.NewReader(out)}

	if _, err := bridge.send("ping", nil); err != nil {
		return fmt.Errorf("worker did not come up: %w", err)
	}
	return nil
}

func Downbridge() {
	if bridge == nil {
		return
	}
	bridge.in.Close()
	bridge.cmd.Wait()
}

func (b *Bridge) send(cmd string, payload any) (json.RawMessage, error) {
	b.mu.Lock()
	defer b.mu.Unlock()

	b.seq++
	line, _ := json.Marshal(map[string]any{"id": b.seq, "cmd": cmd, "payload": payload})

	if _, err := b.in.Write(append(line, '\n')); err != nil {
		return nil, fmt.Errorf("worker gone (write): %w", err)
	}

	raw, err := b.out.ReadBytes('\n')
	if err != nil {
		return nil, fmt.Errorf("worker gone (read): %w", err)
	}

	var r struct {
		Prob json.RawMessage `json:"prob"`
	}
	if err := json.Unmarshal(bytes.TrimSpace(raw), &r); err != nil {
		return nil, fmt.Errorf("bad reply %q: %w", raw, err)
	}
	if len(r.Prob) == 0 || string(r.Prob) == "null" {
		return nil, fmt.Errorf("worker returned null for %q", cmd)
	}
	return r.Prob, nil
}

func (b *Bridge) call(cmd string, payload any) (float64, error) {
	raw, err := b.send(cmd, payload)
	if err != nil {
		return 0, err
	}
	var f float64
	if err := json.Unmarshal(raw, &f); err != nil {
		return 0, fmt.Errorf("bad prob %s for %q", raw, cmd)
	}
	return f, nil
}


func PredictClinical(c *gin.Context) {
	var in entity.Clinical
	c.ShouldBindJSON(&in)

	p, err := bridge.call("predict_clinical", in)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"clinical_prob": p})
}


func PredictGenomic(c *gin.Context) {
	var in entity.Genomic
	c.ShouldBindJSON(&in)

	p, err := bridge.call("predict_genomic", in)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"genomic_prob": p})
}


func PredictBoth(c *gin.Context) {
	var in struct {
		Clinical entity.Clinical `json:"clinical"`
		Genomic  entity.Genomic  `json:"genomic"`
	}
	c.ShouldBindJSON(&in)

	cp, err := bridge.call("predict_clinical", in.Clinical)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	gp, err := bridge.call("predict_genomic", in.Genomic)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}


	c.JSON(http.StatusOK, gin.H{
		"clinical_prob": cp,
		"genomic_prob":  gp,
		"fused_prob":    nil,
	})
}


func Health(c *gin.Context) {
	if _, err := bridge.send("ping", nil); err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"python": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"python": "ok"})
}