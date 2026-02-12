from langgraph.graph import StateGraph, START, END
from nodes.image_generation_node import generate_and_place_images
from nodes.merging_node import decide_images
from nodes.merging_node import merge_content
from nodes.Route_Node import Router_Node, route_next
from nodes.Worker_node import worker_node
from nodes.orches_node import orchestrator_node, fanout
from state.State import Blog_State
from nodes.tavily_research import research_node

# build reducer subgraph
reducer_graph=StateGraph(Blog_State)
reducer_graph.add_node("merge_content", merge_content)
reducer_graph.add_node("decide_images", decide_images)
reducer_graph.add_node("generate_and_place_images", generate_and_place_images)

reducer_graph.add_edge(START, "merge_content")
reducer_graph.add_edge("merge_content", "decide_images")
reducer_graph.add_edge("decide_images", "generate_and_place_images")
reducer_graph.add_edge("generate_and_place_images", END)
reducer_subgraph=reducer_graph.compile()

#--------------  BUILD MAIN GRAPH

g=StateGraph(Blog_State)
g.add_node("router", Router_Node)
g.add_node("research", research_node)
g.add_node("orchestrator", orchestrator_node)
g.add_node("worker", worker_node)
g.add_node("reducer", reducer_subgraph)

# Add edges
g.add_edge(START, "router")
g.add_conditional_edges("router", route_next)
g.add_edge("research", "orchestrator")
# Use fanout for parallel worker execution
# The fanout function returns Send objects which LangGraph handles automatically
# We need to add an edge that triggers fanout - using add_edge with fanout
g.add_edge("orchestrator", "worker")
# After all workers complete, go to reducer
g.add_edge("worker", "reducer")
g.add_edge("reducer", END)

# Compile the graph
app = g.compile()
