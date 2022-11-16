from typing import List, Tuple, Union

import networkx as nx
import plotly.graph_objects as go
from plotly import callbacks


def plot(
    G,
    title: str = "Graph",
    layout: str = None,
    size_method: str = "degree",
    color_method: str = "degree",
    node_label: str = None,
    node_label_position: str = "bottom center",
    node_text: List[str] = None,
    edge_label: str = None,
    edge_label_position: str = "middle center",
    edge_text: List[str] = None,
    titlefont_size: int = 16,
    showlegend: bool = False,
    annotation_text: str = None,
    colorscale: str = "YlGnBu",
    colorbar_title: str = None,
    node_opacity: float = 0.8,
    arrow_size: int = 2,
    transparent_background: bool = True,
    highlight_neighbours_on_hover: bool = True,
    figure_layout: dict = None,
    node_style: dict = None,
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
        Graph annotation text, by default None

    colorscale : {'Greys', 'YlGnBu', 'Greens', 'YlOrRd', 'Bluered', 'RdBu', 'Reds', 'Blues', 'Picnic', 'Rainbow', 'Portland', 'Jet', 'Hot', 'Blackbody', 'Earth', 'Electric', 'Viridis'}
        Scale of the color bar

    colorbar_title : str, optional
        Color bar axis title, by default None

    node_opacity : int, optional
        Opacity of the nodes (1 - filled in, 0 completely transparent), by default 1

    arrow_size : int, optional
        Size of the arrow for Directed Graphs and MultiGraphs, by default 2.

    transparent_background : bool, optional
        True to have a transparent background, by default True

    highlight_neighbours_on_hover : bool, optional
        True to highlight the neighbours of a node on hover, by default True

    Returns
    -------
    Plotly Figure
        Plotly figure of the graph
    """

    plot = PlotGraph(G, layout)

    node_trace = plot.generate_node_traces(
        colorscale=colorscale,
        colorbar_title=colorbar_title,
        color_method=color_method,
        node_label=node_label,
        node_text=node_text,
        node_label_position=node_label_position,
        node_opacity=node_opacity,
        size_method=size_method,
    )

    edge_trace, middle_node_trace = plot.generate_edge_traces(
        edge_label=edge_label,
        edge_label_position=edge_label_position,
        edge_text=edge_text,
    )

    return plot.generate_figure(
        node_trace,
        edge_trace,
        middle_node_trace,
        title=title,
        titlefont_size=titlefont_size,
        showlegend=showlegend,
        annotation_text=annotation_text,
        arrow_size=arrow_size,
        transparent_background=transparent_background,
        highlight_neighbours_on_hover=highlight_neighbours_on_hover,
        figure_layout=figure_layout if figure_layout is not None else {},
        node_style=node_style if node_style is not None else {},
    )


class PlotGraph:
    def __init__(self, G: nx.Graph, layout: str):
        """
        PlotGraph is a class that plots a graph.
        """
        self.G: nx.Graph = G
        self.layout = layout

        if layout:
            self.pos_dict = self._apply_layout(G, layout)
        elif not nx.get_node_attributes(G, "pos"):
            self.pos_dict = self._apply_layout(G, "random")
        else:
            self.pos_dict = nx.get_node_attributes(G, "pos")

        self.inverse_pos_dict = {(v[0], v[1]): k for k, v in self.pos_dict.items()}

    def generate_node_traces(
        self,
        colorscale: str,
        colorbar_title: str,
        color_method: Union[str, List[str]],
        node_label: str,
        node_text: List[str],
        node_label_position: str,
        node_opacity: float,
        size_method: Union[str, List[str]],
    ):

        node_mode = "markers+text" if node_label else "markers"
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
                    thickness=15,
                    title=colorbar_title,
                    xanchor="left",
                    titleside="right",
                ),
                line_width=0,
                opacity=node_opacity,
            ),
        )

        for node in self.G.nodes():
            text = f"Node: {node}<br>Degree: {self.G.degree(node)}"
            x, y = self.G.nodes[node]["pos"]

            node_trace["x"] += (x,)
            node_trace["y"] += (y,)

            if node_label:
                node_trace["text"] += (self.G.nodes[node][node_label],)
            if node_text:
                for prop in node_text:
                    text += f"<br></br>{prop}: {self.G.nodes[node][prop]}"
            node_trace["hovertext"] += (text.strip(),)

            if isinstance(size_method, list):
                node_trace["marker"]["size"] = size_method
            elif size_method == "degree":
                node_trace["marker"]["size"] += (self.G.degree(node) + 12,)
            elif size_method == "static":
                node_trace["marker"]["size"] += (28,)
            else:
                node_trace["marker"]["size"] += (self.G.nodes[node][size_method],)

            if isinstance(color_method, list):
                node_trace["marker"]["color"] = color_method
            elif color_method == "degree":
                node_trace["marker"]["color"] += (self.G.degree(node),)
            else:
                node_trace["marker"]["color"] += (
                    (self.G.nodes[node][color_method],)
                    if color_method in self.G.nodes[node]
                    else (color_method,)
                )

        return node_trace

    def generate_edge_traces(
        self, edge_label: str, edge_label_position: str, edge_text: List[str]
    ) -> Tuple[go.Scatter, go.Scatter]:
        """
        Generates the edge traces for the graph.

        Parameters
        ----------
        edge_label : str, optional
            Edge property to be shown on the edge.


        edge_label_position: str, optional
            Position of the edge label.
            Either {'top left', 'top center', 'top right', 'middle left',
                'middle center', 'middle right', 'bottom left', 'bottom
                center', 'bottom right'}

        edge_text : list, optional
            A list of edge properties to display when hovering over the edge.

        Returns
        -------
        Tuple[go.Scatter, go.Scatter]
            Lines and invisible nodes for the edges.
        """

        edge_mode = "lines+text" if edge_label else "lines"
        edge_text_list = []
        edge_properties = {}

        # This trace is for the actual lines that appear on the plot
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=1, color="#888"),
            text=[],
            hoverinfo="text",
            mode=edge_mode,
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

        for edge in self.G.edges(data=True):
            x0, y0 = self.G.nodes[edge[0]]["pos"]
            x1, y1 = self.G.nodes[edge[1]]["pos"]
            edge_trace["x"] += (x0, x1, None)
            edge_trace["y"] += (y0, y1, None)

            if edge_text or edge_label:
                edge_pair = edge[0], edge[1]
                if edge_pair not in edge_properties:
                    edge_properties[edge_pair] = {}
                    middle_node_trace["x"] += ((x0 + x1) / 2,)
                    middle_node_trace["y"] += ((y0 + y1) / 2,)

            if edge_text:
                for prop in edge_text:
                    if edge[2][prop] not in edge_properties[edge_pair]:
                        edge_properties[edge_pair][prop] = []
                edge_properties[edge_pair][prop] += [edge[2][prop]]

            if edge_label:
                middle_node_trace["text"] += (edge[2][edge_label],)
                middle_node_trace["mode"] = "markers+text"

        if edge_text:
            edge_text_list = [
                "\n".join(f"{k}: {v}" for k, v in vals.items())
                for _, vals in edge_properties.items()
            ]

            middle_node_trace["hovertext"] = edge_text_list

        return edge_trace, middle_node_trace

    def generate_figure(
        self,
        node_trace: go.Scatter,
        edge_trace: go.Scatter,
        middle_node_trace: go.Scatter,
        title: str,
        titlefont_size: int,
        showlegend: bool,
        annotation_text,
        arrow_size: int,
        transparent_background: bool,
        highlight_neighbours_on_hover: bool,
        figure_layout: dict,
        node_layout: dict,
    ):
        """
        Helper function to generate the figure for the Graph.
        """

        if not annotation_text:
            annotation_text = ""

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

        if isinstance(self.G, (nx.DiGraph, nx.MultiDiGraph)):
            annotations.extend(
                dict(
                    ax=self.G.nodes[edge[0]]["pos"][0],
                    ay=self.G.nodes[edge[0]]["pos"][1],
                    axref="x",
                    ayref="y",
                    x=self.G.nodes[edge[1]]["pos"][0] * 0.85
                    + self.G.nodes[edge[0]]["pos"][0] * 0.15,
                    y=self.G.nodes[edge[1]]["pos"][1] * 0.85
                    + self.G.nodes[edge[0]]["pos"][1] * 0.15,
                    xref="x",
                    yref="y",
                    showarrow=True,
                    arrowhead=1,
                    arrowsize=arrow_size,
                )
                for edge in self.G.edges()
            )

        node_trace.update(**node_style)
        self.f = go.FigureWidget(
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
                **figure_layout,
            ),
        )

        if transparent_background:
            self.f.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
            )

        if highlight_neighbours_on_hover:
            self.original_node_trace = node_trace

            self.f.data[1].on_hover(self.on_hover)
            self.f.data[1].on_unhover(self.on_unhover)

        return self.f

    def _apply_layout(self, G, layout):
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

        return pos_dict

    def on_hover(
        self,
        trace: go.Scatter,
        points: callbacks.Points,
        input_device_state: callbacks.InputDeviceState,
    ):
        """
        Callback function for when a node is hovered over.

        Parameters
        ----------
        trace : go.Scatter
            Figure trace for the node.
        points : callbacks.Points
            Points that are hovered over.
        input_device_state : callbacks.InputDeviceState
            Input device state, e.g. what keys were pressed
        """

        if not points.point_inds:
            return

        node = self.inverse_pos_dict[(points.xs[0], points.ys[0])]

        neighbours = list(self.G.neighbors(node))

        node_colours = list(trace.marker.color)

        new_colors = ["#E4E4E4"] * len(node_colours)

        new_colors[points.point_inds[0]] = node_colours[points.point_inds[0]]

        for neighbour in neighbours:
            trace_position = list(self.pos_dict).index(neighbour)
            new_colors[trace_position] = node_colours[trace_position]

        with self.f.batch_update():
            trace.marker.color = new_colors

    def on_unhover(
        self,
        trace: go.Scatter,
        points: callbacks.Points,
        input_device_state: callbacks.InputDeviceState,
    ):
        """
        Callback function for when a node is unhovered over.

        Parameters
        ----------
        trace : go.Scatter
            Figure trace for the node.
        points : callbacks.Points
            Points that are hovered over.
        input_device_state : callbacks.InputDeviceState
            Input device state, e.g. what keys were pressed
        """

        with self.f.batch_update():
            trace.marker.color = self.original_node_trace.marker.color
            trace.marker.size = self.original_node_trace.marker.size
