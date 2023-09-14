import networkx as nx
import plotly.graph_objects as go


def draw_jet_graph(G, title='a jet'):
    node_x = [attrs.get('p', (0,0,0))[0] for node, attrs in G.nodes(data=True)]
    node_y = [attrs.get('p', (0,0,0))[1] for node, attrs in G.nodes(data=True)]
    node_z = [attrs.get('p', (0,0,0))[2] for node, attrs in G.nodes(data=True)]

    edge_x = []
    edge_y = []
    edge_z = []

    for s, e, attrs in G.edges(data=True):
        x0 = G.nodes()[s]['p'][0]
        x1 = G.nodes()[e]['p'][0]
    
        y0 = G.nodes()[s]['p'][1]
        y1 = G.nodes()[e]['p'][1]
    
        z0 = G.nodes()[s]['p'][2]
        z1 = G.nodes()[e]['p'][2]
    
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

    # node_color = [a['p'][2] for n, a in G.nodes(data=True)]
    node_color = [a['color'] for n, a in G.nodes(data=True)]
    node_text = ['pT={} (GeV/c)'.format(v) for v in node_color]
    node_symbols = [a['symbol'] for n, a in G.nodes(data=True)]
    node_sizes = [a['size'] for n, a in G.nodes(data=True)]
    
    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(color='gray', width=1),
        hoverinfo='none'
    )

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers',
        marker=dict(
            showscale=False,
            colorscale='Viridis',
            size=node_sizes,
            # colorbar=dict(
            #     thickness=20,
            #     # title=r'$p_{T}$ (GeV/c)',
            #     title='pT (GeV/c)',
            #     xanchor='left',
            #     titleside='right'
            # ),
            line_width=2,
            color=node_color,
            symbol=node_symbols
        ),
        text=node_text,
        hoverinfo='text'
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=title,
                        scene=dict(
                            xaxis=dict(visible=False),
                            yaxis=dict(visible=False),
                            zaxis=dict(visible=True)
                        )
                    ))

    fig.update_layout(width=800, height=600, showlegend=False)
    # fig.update_layout(scene=dict(zaxis_title=r"$p_{T}$"))
    fig.update_layout(scene=dict(zaxis_title='pT (GeV/c)'))
    
    fig.show()
    return fig