--------------------------------------
# Checkpointers : Short Term Memory
--------------------------------------

## Checkpointers
Checkpointers are used to store the state of the graph after every single super step.
At the boundary of every single super step, checkpointers save a snapshot of the graph.


## Super Step
Super step is a round of execution, which can contain one or more nodes.
Execution begins upon the call to the invoke() function.

## Checkpoints
Checkpoints are the individual snapshots at a single moment in time.


## Thread
Thread(s) use thread_id to store a series of checkpoints.

## Summary
- Superstep is the action/tick of executing the node(s).
- Checkpointers is the photograph at an instant in time of the graph, after super step finishes.
- Thread is the album.