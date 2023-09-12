import networkx as nx
import plotly.graph_objects as go


class JetGraph(object):
	def __init__(self, j):
		self.j = j
		self.G = nx.Graph()
		self.n = 0
		self.max_depth = 0
		self.max_depth = self.get_max_depth(j, 0)
		self.add_sj(j, -1, self.max_depth)
  
	def get_max_depth(self, sj, depth):
		p1 = fj.PseudoJet()
		p2 = fj.PseudoJet()
		depth = depth + 1
		if sj.has_parents(p1, p2):
			_ = self.get_max_depth(p1, depth)
			_ = self.get_max_depth(p2, depth)
		if depth > self.max_depth:	
			self.max_depth = depth
		return self.max_depth
   
	def add_sj(self, sj, parent_n, depth):
		p1 = fj.PseudoJet()
		p2 = fj.PseudoJet()
		self.n = self.n + 1
		this_n = self.n
		dphi = self.j.delta_phi_to(sj)
		deta = self.j.eta() - sj.eta()
		if sj.has_parents(p1, p2):
			# self.G.add_node(this_n, color='red', p=(sj.px(), sj.py(), sj.pz()))
			# self.G.add_node(this_n, color='red', p=(sj.phi(), sj.eta(), sj.perp()))
			self.G.add_node(this_n, color='red', p=(dphi, deta, sj.perp()), symbol='square-open', size=15)
			if parent_n > 0:
				self.G.add_edge(this_n, parent_n, color='green')
			self.add_sj(p1, this_n, depth)
			self.add_sj(p2, this_n, depth)
		else:
			self.G.add_node(this_n, color='blue', p=(dphi, deta, sj.perp()), symbol='circle', size=15)
			if parent_n > 0:
				self.G.add_edge(this_n, parent_n, color='green')

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
            showscale=True,
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