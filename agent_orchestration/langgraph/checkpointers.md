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

## GetState
The graph.get_state() is used to fetch the latest checkpoint information:
 - metadata
 - checkpointID
 - next node
 - value of the node
 - config
 - tasks


 ## GetStateHistory
 The graph.get_state_history() is used to fetch the entire history of all checkpoints in the graph.
 The most recent one displayed first.


## UpdateState
The graph.update_state() will create a new checkpoint from either the last checkpoint or a checkpoint in the history, the graph is forked, and upon a new execution path is taken.



## Replay
Replay allows to run a node or set of nodes after a particular checkpoint in history, nodes before this checkpointer are ignored.