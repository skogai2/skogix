---
title: intentions
type: reference
permalink: skogai-routing/intentions
---

# What skogai-routing is for

This is my reading of the intentions, ideas and open questions behind the project. It is a starting point to correct, not a finished position.

## The problem

Agents need a lot of guidance: instructions, procedures, facts, output shapes. Loading all of it into every session wastes room and buries the part that matters. Loading none of it means the agent improvises. The question is how to make guidance findable by a reader who doesn't already know where it lives.

## The core intention

Guidance is a set of small, purposeful pieces connected by explicit pointers. Each piece says where to go next. A reader starts at one place, makes a choice, takes one step, and stops once it has what the task needs.

## Ideas behind it

- **Navigation over loading.** The entry point is short. It routes; it does not teach.
- **Ownership as the backbone.** Every piece belongs to something. The owner is the one place that says what this piece is for and who keeps it true. Meaning does not pass down through a chain of owners; each step is taken on its own.
- **Recognizable by name.** A starting point should be identifiable from its name alone, so a person or an agent scanning a folder knows where to begin without opening anything.
- **One job per piece.** A piece that routes, instructs, explains and templates at once gets split. The jobs are: route, procedure, fact, output shape, repeatable check.
- **Deliberately small scope.** The first version proves only the routing step. Everything else waits until routing is trusted.
- **Plain text first.** A person should be able to read it with nothing but a text editor.
- **Checks as guard rails.** Validation keeps starting points small and well-formed. It does not define what the guidance means.

## How it fits the wider picture

- **Navigation and knowledge are separate jobs.** This project answers "where should I look next?" Something else answers "what is true?" A knowledge bundle could sit underneath as the material the routes lead to.
- **It formalizes what already happens informally.** Per-project starting points, a root entry, and pointers outward are already how the personal setup works. The project's job is to make that explicit and checkable.

