import plotly.graph_objects as go
import networkx as nx
from typing import Union


def plot(
    G,
    title="Graph",
    layout=None,
    size_method="degree",
    color_method="degree",
    node_label="",
    node_label_position="bottom center",
    node_text=[],
    edge_label="",
    edge_label_position="middle center",
    edge_text=[],
    titlefont_size=16,
    showlegend=False,
    annotation_text="",
    colorscale="YlGnBu",
    colorbar_title="",
    node_opacity=1,
    arrow_size=2,
):
    """
    Plots a Graph using Plotly.
    
    Parameters
    ----------
    G : Networkx Graph
        Network Graph

    title : str, optional
        Title of the graph, by default "Graph"

    layout : {"random", "circular", "kamada", "planar", "spring", "spectral", "spiral"}, optional
        Layout of the nodes on the plot.

            random (default): Position nodes uniformly at random in the unit square.
                For every node, a position is generated by choosing each of dim coordinates uniformly at random on the interval [0.0, 1.0).
            
            circular: Position nodes on a circle.
            
            kamada: Position nodes using Kamada-Kawai path-length cost-function.
            
            planar: Position nodes without edge intersections, if possible (if the Graph is planar).
            
            spring: Position nodes using Fruchterman-Reingold force-directed algorithm.
            
            spectral: Position nodes using the eigenvectors of the graph Laplacian.
            
            spiral: Position nodes in a spiral layout.
            
    size_method : {'degree', 'static'}, node property or a list, optional
        How to size the nodes., by default "degree"

            degree: The larger the degree, the larger the node.

            static: All nodes are the same size.

            node property: A property field of the node.

            list: A list pertaining to the size of the nodes.

    color_method : {'degree'}, hex color code, node property, or list optional
        How to color the node., by default "degree"

            degree: Color the nodes based on their degree.

            hex color code: Hex color code.

            node property: A property field of the node.

            list: A list pertaining to the colour of the nodes.

    node_label : str, optional
        Node property to be shown on the node.

    node_label_position: str, optional
        Position of the node label.
        Either {'top left', 'top center', 'top right', 'middle left',
            'middle center', 'middle right', 'bottom left', 'bottom
            center', 'bottom right'}

    node_text : list, optional
        A list of node properties to display when hovering over the node.

    edge_text : list, optional
        A list of edge properties to display when hovering over the edge.
    
    edge_label : str, optional
        Edge property to be shown on the edge.

    edge_label_position: str, optional
        Position of the edge label.
        Either {'top left', 'top center', 'top right', 'middle left',
            'middle center', 'middle right', 'bottom left', 'bottom
            center', 'bottom right'}

    titlefont_size : int, optional
        Font size of the title, by default 16

    showlegend : bool, optional
        True to show legend, by default False

    annotation_text : str, optional
        Graph annotation text, by default ""

    colorscale : {'Greys', 'YlGnBu', 'Greens', 'YlOrRd', 'Bluered', 'RdBu', 'Reds', 'Blues', 'Picnic', 'Rainbow', 'Portland', 'Jet', 'Hot', 'Blackbody', 'Earth', 'Electric', 'Viridis'}
        Scale of the color bar

    colorbar_title : str, optional
        Color bar axis title, by default ""

    node_opacity : int, optional
        Opacity of the nodes (1 - filled in, 0 completely transparent), by default 1

    arrow_size : int, optional
        Size of the arrow for Directed Graphs and MultiGraphs, by default 2.
    
    Returns
    -------
    Plotly Figure
        Plotly figure of the graph
    """

    if layout:
        _apply_layout(G, layout)
    elif not nx.get_node_attributes(G, "pos"):
        _apply_layout(G, "random")

    node_trace, edge_trace, middle_node_trace = _generate_scatter_trace(
        G,
        size_method=size_method,
        color_method=color_method,
        colorscale=colorscale,
        colorbar_title=colorbar_title,
        node_label=node_label,
        node_label_position=node_label_position,
        node_text=node_text,
        edge_label=edge_label,
        edge_label_position=edge_label_position,
        edge_text=edge_text,
        node_opacity=1,
    )

    fig = _generate_figure(
        G,
        node_trace,
        edge_trace,
        middle_node_trace,
        title=title,
        titlefont_size=titlefont_size,
        showlegend=showlegend,
        annotation_text=annotation_text,
        arrow_size=arrow_size,
    )

    return fig


def _generate_scatter_trace(
    G,
    size_method: Union[str, list],
    color_method: Union[str, list],
    colorscale: str,
    colorbar_title: str,
    node_label: str,
    node_label_position: str,
    node_text: list,
    edge_label: str,
    edge_label_position: str,
    edge_text: bool,
    node_opacity: int,
):
    """
    Helper function to generate Scatter plot traces for the graph.
    """

    edge_text_list = []
    edge_properties = {}

    node_mode = "markers" if not node_label else "markers+text"
    edge_mode = "lines" if not edge_label else "lines+text"

    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=2, color="#888"),
        text=[],
        hoverinfo="text",
        mode="lines",
    )

    # NOTE: This is a hack because Plotly does not allow you to have hover text on a line
    # Were adding an invisible node to the edges that will display the edge properties
    middle_node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        hoverinfo="text",
        textposition=edge_label_position,
        marker=dict(opacity=0),
    )

    node_trace = go.Scatter(
        x=[],
        y=[],
        mode=node_mode,
        text=[],
        hovertext=[],
        hoverinfo="text",
        textposition=node_label_position,
        marker=dict(
            showscale=True,
            colorscale=colorscale,
            reversescale=True,
            size=[],
            color=[],
            colorbar=dict(
                thickness=15, title=colorbar_title, xanchor="left", titleside="right"
            ),
            line_width=2,
            opacity=node_opacity,
        ),
    )

    for edge in G.edges(data=True):
        x0, y0 = G.nodes[edge[0]]["pos"]
        x1, y1 = G.nodes[edge[1]]["pos"]
        edge_trace["x"] += tuple([x0, x1, None])
        edge_trace["y"] += tuple([y0, y1, None])

        if edge_text or edge_label:
            # Now we can add the text
            # First we need to aggregate all the properties for each edge
            edge_pair = (edge[0], edge[1])
            # if an edge property for an edge hasn't been tracked, add an entry
            if edge_pair not in edge_properties:
                edge_properties[edge_pair] = {}

                # Since we haven't seen this node combination before also add it to the trace
                middle_node_trace["x"] += tuple([(x0 + x1) / 2])
                middle_node_trace["y"] += tuple([(y0 + y1) / 2])

            # For each edge property, create an entry for that edge, keeping track of the property name and its values
            # If it doesn't exist, add an entry
            if edge_text:
                for prop in edge_text:
                    if edge[2][prop] not in edge_properties[edge_pair]:
                        edge_properties[edge_pair][prop] = []

                edge_properties[edge_pair][prop] += [edge[2][prop]]

            if edge_label:
                middle_node_trace["text"] += tuple([edge[2][edge_label]])
                middle_node_trace["mode"] = "markers+text"

    if edge_text:
        edge_text_list = [
            "\n".join(f"{k}: {v}" for k, v in vals.items())
            for _, vals in edge_properties.items()
        ]

        middle_node_trace["hovertext"] = edge_text_list

    for node in G.nodes():
        text = f"Node: {node}<br>Degree: {G.degree(node)}"

        x, y = G.nodes[node]["pos"]
        node_trace["x"] += tuple([x])
        node_trace["y"] += tuple([y])

        if node_label:
            node_trace["text"] += tuple([G.nodes[node][node_label]])

        if node_text:
            for prop in node_text:
                text += f"<br></br>{prop}: {G.nodes[node][prop]}"

        node_trace["hovertext"] += tuple([text.strip()])

        if isinstance(size_method, list):
            node_trace["marker"]["size"] = size_method
        else:
            if size_method == "degree":
                node_trace["marker"]["size"] += tuple([G.degree(node) + 12])
            elif size_method == "static":
                node_trace["marker"]["size"] += tuple([28])
            else:
                node_trace["marker"]["size"] += tuple([G.nodes[node][size_method]])

        if isinstance(color_method, list):
            node_trace["marker"]["color"] = color_method
        else:
            if color_method == "degree":
                node_trace["marker"]["color"] += tuple([G.degree(node)])
            else:
                # Look for the property, otherwise look for a color code
                # If none exist, throw an error
                if color_method in G.nodes[node]:
                    node_trace["marker"]["color"] += tuple(
                        [G.nodes[node][color_method]]
                    )
                else:
                    node_trace["marker"]["color"] += tuple([color_method])

    return node_trace, edge_trace, middle_node_trace


def _generate_figure(
    G,
    node_trace,
    edge_trace,
    middle_node_trace,
    title,
    titlefont_size,
    showlegend,
    annotation_text,
    arrow_size,
):
    """
    Helper function to generate the figure for the Graph.
    """

    annotations = [
        dict(
            text=annotation_text,
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.005,
            y=-0.002,
        )
    ]

    if isinstance(G, (nx.DiGraph, nx.MultiDiGraph)):

        for edge in G.edges():
            annotations.append(
                dict(
                    ax=G.nodes[edge[0]]["pos"][0],
                    ay=G.nodes[edge[0]]["pos"][1],
                    axref="x",
                    ayref="y",
                    x=(
                        G.nodes[edge[1]]["pos"][0] * 0.85
                        + G.nodes[edge[0]]["pos"][0] * 0.15
                    ),
                    y=(
                        G.nodes[edge[1]]["pos"][1] * 0.85
                        + G.nodes[edge[0]]["pos"][1] * 0.15
                    ),
                    xref="x",
                    yref="y",
                    showarrow=True,
                    arrowhead=1,
                    arrowsize=arrow_size,
                    # arrowwidth=1.5,
                )
            )

    fig = go.Figure(
        data=[edge_trace, node_trace, middle_node_trace],
        layout=go.Layout(
            title=title,
            titlefont_size=titlefont_size,
            showlegend=showlegend,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=annotations,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    return fig


def _apply_layout(G, layout):
    """
    Applies a layout to a Graph.
    """

    layout_functions = {
        "random": nx.random_layout,
        "circular": nx.circular_layout,
        "kamada": nx.kamada_kawai_layout,
        "planar": nx.planar_layout,
        "spring": nx.spring_layout,
        "spectral": nx.spectral_layout,
        "spiral": nx.spiral_layout,
    }

    pos_dict = layout_functions[layout](G)

    nx.set_node_attributes(G, pos_dict, "pos")
