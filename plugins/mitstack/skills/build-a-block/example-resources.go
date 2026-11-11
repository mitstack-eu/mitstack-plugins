package main

// resources.go is the one file you write: a type with Ensure, Observe and Delete for each resource manifest.yaml declares, listed by name in resources.

import (
	"context"
	"fmt"
	"net/http"
	"net/url"
	"strings"

	"github.com/mitstack-eu/block-kit/capabilities/github/ghapi"
	"github.com/mitstack-eu/block-kit/contract"
)

var resources = map[string]githubResource{
	"github.repository": repository{suffix: "app"},
}

// repository is a github.repository in the connected account, named for the subscription and its suffix.
type repository struct {
	suffix string
}

// Ensure creates the repository unless an earlier subscribe made it, tags it with the subscription, and returns its identity.
func (r repository) Ensure(ctx context.Context, gh *ghapi.Client, d contract.Desired) (map[string]string, error) {
	owner, name := r.named(d)
	repo, err := ghapi.SafeRepo(owner + "/" + name)
	if err != nil {
		return nil, err
	}
	status, err := callGitHub(ctx, gh, http.MethodGet, "/repos/"+repo, nil, nil)
	if err != nil {
		return nil, err
	}
	if status == http.StatusNotFound {
		body := map[string]any{"name": name, "private": true}
		status, err = callGitHub(ctx, gh, http.MethodPost, "/orgs/"+url.PathEscape(owner)+"/repos", body, nil)
		if err != nil {
			return nil, err
		}
		if status != http.StatusCreated {
			return nil, fmt.Errorf("creating %s: github answered %d", repo, status)
		}
	} else if status != http.StatusOK {
		return nil, fmt.Errorf("reading %s: github answered %d", repo, status)
	}
	if err := tagRepository(ctx, gh, repo, d.SubscriptionID); err != nil {
		return nil, err
	}
	return map[string]string{"repo": repo}, nil
}

// named gives the owner and name Ensure creates the repository under.
func (r repository) named(d contract.Desired) (owner, name string) {
	return ghapi.Owner(d), strings.ReplaceAll(d.SubscriptionID, "_", "-") + "-" + r.suffix
}

// Observe reports the repository present with its "repo" output, or absent when GitHub answers 404; with no identity it reads the name Ensure gives, as a create that failed before recording one leaves.
func (r repository) Observe(ctx context.Context, gh *ghapi.Client, ref contract.ResourceRef) (contract.Observation, error) {
	id := ref.Identity["repo"]
	if id == "" {
		owner, name := r.named(ref.Desired)
		id = owner + "/" + name
	}
	repo, err := ghapi.SafeRepo(id)
	if err != nil {
		return contract.Observation{}, err
	}
	status, err := callGitHub(ctx, gh, http.MethodGet, "/repos/"+repo, nil, nil)
	switch {
	case err != nil:
		return contract.Observation{}, err
	case status == http.StatusNotFound:
		return contract.Observation{State: contract.Absent, Outputs: map[string]string{}}, nil
	case status != http.StatusOK:
		return contract.Observation{}, fmt.Errorf("reading %s: github answered %d", repo, status)
	}
	return contract.Observation{State: contract.Present, Outputs: map[string]string{"repo": repo}}, nil
}

// Delete deletes the repository at ref.Identity, and one already gone is success.
func (repository) Delete(ctx context.Context, gh *ghapi.Client, ref contract.ResourceRef) error {
	repo, err := ghapi.SafeRepo(ref.Identity["repo"])
	if err != nil {
		return err
	}
	status, err := callGitHub(ctx, gh, http.MethodDelete, "/repos/"+repo, nil, nil)
	if err != nil {
		return err
	}
	if status != http.StatusNoContent && status != http.StatusNotFound {
		return fmt.Errorf("deleting %s: github answered %d", repo, status)
	}
	return nil
}
