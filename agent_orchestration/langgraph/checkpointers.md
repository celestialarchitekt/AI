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



## Replay
Replay allows to run a node or set of nodes after a particular checkpoint in history, nodes before this checkpointer are ignored.



## UpdateState
The graph.update_state() will create a new checkpoint from either the last checkpoint or a checkpoint in the history, the graph is forked, and upon a new execution path is taken.


🧠 LangGraph State & Time-Travel: Key Lessons Learned

Here is a summary of the core mechanics and insights mastered during this session:
1. Checkpoint History & Indexing

    Newest-First Order: graph.get_state_history() always returns a list sorted from newest to oldest.

    history[0] is King: Index 0 is always your absolute latest checkpoint—whether it was generated naturally by a node finishing or manually via update_state().

2. Forking, Not Overwriting

    Immutability: Calling update_state() on a historical checkpoint never destroys past data. Instead, it creates a brand-new, child checkpoint (a fork), enabling true temporal branching and "what-if" scenarios.

3. The Config Hand-Off Rule

    Capture the New Config: graph.update_state() returns a new config pointing directly to your freshly created fork.

    The Gotcha: If you pass an old historical config into graph.invoke(None, past_config), the graph will execute on the old timeline. You must pass the config returned by update_state() to walk down your new branch.

4. Queue Behavior & Downstream Overwrites

    Queued Tasks Run: When you fork from a past checkpoint (e.g., right after node_a), whatever nodes were left in the queue (node_b) will still run automatically when you invoke execution.

    Node Logic Trumps Manual Injections: Without reducers, regular state fields are replaced by whatever a node explicitly returns. If node_b hardcodes return {"foo": "original_value"}, it will wipe out any manual overrides you injected unless node_b is designed to leave those fields alone or build upon them.



