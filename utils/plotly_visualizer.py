#!/usr/bin/env python3
"""
Knowledge Graph Traversal 3D Visualizer with Plotly
==================================================

Creates beautiful 3D visualizations of semantic graph traversal for all four algorithms.
Adapted from perfect reference examples to work with algorithm results and cached embeddings.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import time

from .algos.base_algorithm import RetrievalResult
from .traversal import TraversalPath, GranularityLevel, ConnectionType
from .knowledge_graph import KnowledgeGraph


@dataclass
class VisualizationNode:
    """Node information for visualization"""
    node_id: str
    node_type: str  # 'chunk', 'sentence', or 'query'
    text: str
    embedding: np.ndarray
    step_number: int
    relevance_score: float
    connection_type: str
    distance_from_anchor: int
    document_id: str
    is_final_result: bool


class KnowledgeGraphPlotlyVisualizer:
    """Create 3D visualizations of knowledge graph traversal using Plotly"""

    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph

    def visualize_retrieval_result(self, result: RetrievalResult, query: str,
                                   method: str = "pca", max_nodes: int = 50,
                                   show_all_visited: bool = True,
                                   edge_threshold: float = 0.75) -> go.Figure:
        """
        Create 3D visualization of algorithm traversal results.
        Matches the style and functionality of the perfect reference examples.
        """
        print(f"🎨 Creating 3D visualization for {result.algorithm_name}")

        # Extract visualization nodes from the result and knowledge graph
        nodes = self._extract_visualization_nodes(result, query, show_all_visited)
        
        if len(nodes) < 2:
            print(f"⚠️ Only {len(nodes)} nodes found - creating basic visualization")
            return self._create_basic_plotly_visualization(result, query)

        # Limit nodes for performance (like reference examples)
        if len(nodes) > max_nodes:
            # Keep query, first few traversal steps, and all final results
            query_nodes = [n for n in nodes if n.node_type == 'query']
            final_result_nodes = [n for n in nodes if n.is_final_result]
            traversal_nodes = [n for n in nodes if n.node_type != 'query' and not n.is_final_result]
            
            # Keep first traversal nodes up to the limit
            max_traversal = max_nodes - len(query_nodes) - len(final_result_nodes)
            traversal_nodes = traversal_nodes[:max_traversal]
            
            nodes = query_nodes + traversal_nodes + final_result_nodes
            print(f"🎯 Limited to {len(nodes)} nodes for performance")

        # Create the 3D plot (like reference examples)
        return self._create_3d_plot(nodes, result, query, method, edge_threshold)

    def _extract_visualization_nodes(self, result: RetrievalResult, query: str, 
                                   show_all_visited: bool) -> List[VisualizationNode]:
        """Extract all nodes for visualization from result and knowledge graph"""
        nodes = []

        # Add query as a special node (like reference examples)
        query_embedding = self._get_query_embedding(query)
        if query_embedding is not None:
            nodes.append(VisualizationNode(
                node_id="QUERY",
                node_type="query",
                text=query,
                embedding=query_embedding,
                step_number=-1,
                relevance_score=1.0,
                connection_type="query",
                distance_from_anchor=0,
                document_id="QUERY",
                is_final_result=False
            ))

        # Get final result nodes (sentences that were actually retrieved)
        final_result_nodes = self._extract_final_result_nodes(result)
        
        # Get traversal nodes if available and requested
        traversal_nodes = []
        if show_all_visited and result.traversal_path and result.traversal_path.nodes:
            traversal_nodes = self._extract_traversal_nodes(result)

        # Combine all nodes
        nodes.extend(traversal_nodes)
        nodes.extend(final_result_nodes)

        # Mark final results
        final_sentences = set(result.retrieved_content)
        for node in nodes:
            if node.text in final_sentences:
                node.is_final_result = True

        print(f"📊 Extracted {len(nodes)} nodes: {len([n for n in nodes if n.node_type == 'query'])} query, "
              f"{len([n for n in nodes if n.is_final_result])} final results, "
              f"{len([n for n in nodes if not n.is_final_result and n.node_type != 'query'])} traversal")

        return nodes

    def _extract_final_result_nodes(self, result: RetrievalResult) -> List[VisualizationNode]:
        """Extract nodes for the final retrieved content"""
        nodes = []

        for i, sentence_text in enumerate(result.retrieved_content):
            # Try to find this sentence in the knowledge graph
            sentence_id = self._find_sentence_id(sentence_text)
            embedding = None
            document_id = "unknown"

            if sentence_id:
                # Get sentence object and its embedding
                sentence_obj = self.kg.sentences.get(sentence_id)
                if sentence_obj:
                    embedding = self._get_sentence_embedding(sentence_id)
                    document_id = self._get_sentence_document(sentence_obj)
            
            if embedding is None:
                # Fallback: encode the sentence text directly
                embedding = self._encode_text(sentence_text)

            # Calculate relevance score
            relevance_score = result.confidence_scores[i] if i < len(result.confidence_scores) else 0.5
            if hasattr(result, 'query_similarities') and result.query_similarities:
                relevance_score = result.query_similarities.get(sentence_text, relevance_score)

            nodes.append(VisualizationNode(
                node_id=sentence_id or f"sentence_{i}",
                node_type="sentence",
                text=sentence_text,
                embedding=embedding,
                step_number=i,
                relevance_score=relevance_score,
                connection_type="final_result",
                distance_from_anchor=0,
                document_id=document_id,
                is_final_result=True
            ))

        return nodes

    def _extract_traversal_nodes(self, result: RetrievalResult) -> List[VisualizationNode]:
        """Extract nodes from the traversal path"""
        nodes = []

        if not result.traversal_path or not result.traversal_path.nodes:
            return nodes

        path = result.traversal_path

        for i, node_id in enumerate(path.nodes):
            granularity = path.granularity_levels[i] if i < len(path.granularity_levels) else GranularityLevel.CHUNK
            connection_type = path.connection_types[i - 1] if i > 0 and i - 1 < len(path.connection_types) else ConnectionType.RAW_SIMILARITY

            embedding = None
            text = ""
            document_id = "unknown"
            node_type = "chunk"

            if granularity == GranularityLevel.SENTENCE:
                # This is a sentence node
                sentence_obj = self.kg.sentences.get(node_id)
                if sentence_obj:
                    embedding = self._get_sentence_embedding(node_id)
                    text = sentence_obj.sentence_text if hasattr(sentence_obj, 'sentence_text') else str(sentence_obj)
                    document_id = self._get_sentence_document(sentence_obj)
                    node_type = "sentence"
            else:
                # This is a chunk node
                chunk_obj = self.kg.chunks.get(node_id)
                if chunk_obj:
                    embedding = self._get_chunk_embedding(node_id)
                    text = chunk_obj.chunk_text if hasattr(chunk_obj, 'chunk_text') else str(chunk_obj)
                    # Truncate long chunk text for display
                    if len(text) > 100:
                        text = text[:100] + "..."
                    document_id = self._get_chunk_document(node_id)
                    node_type = "chunk"

            if embedding is None:
                # Skip nodes without embeddings
                continue

            # Calculate relevance score
            relevance_score = self._calculate_node_relevance(node_id, result)

            nodes.append(VisualizationNode(
                node_id=node_id,
                node_type=node_type,
                text=text,
                embedding=embedding,
                step_number=i,
                relevance_score=relevance_score,
                connection_type=connection_type.value if hasattr(connection_type, 'value') else str(connection_type),
                distance_from_anchor=i,
                document_id=document_id,
                is_final_result=False
            ))

        return nodes

    def _create_3d_plot(self, nodes: List[VisualizationNode], result: RetrievalResult,
                        query: str, method: str, edge_threshold: float = 0.75) -> go.Figure:
        """Create the 3D scatter plot showing full knowledge graph with traversal path highlighted"""

        if len(nodes) < 2:
            print("❌ Not enough nodes for 3D visualization")
            return self._create_basic_plotly_visualization(result, query)

        # ENHANCEMENT: Load ALL chunks from knowledge graph for full context
        print(f"🌐 Loading full knowledge graph for context...")
        all_kg_chunks = self._get_all_kg_chunks()

        # Get embeddings for ALL chunks in KG (+ query if present)
        all_embeddings = []
        all_chunk_ids = []
        all_chunk_docs = []
        all_chunk_texts = []

        # Add query embedding first if present
        query_in_graph = False
        if nodes and nodes[0].node_type == 'query':
            # Ensure query embedding is a 1D numpy array
            query_embedding = np.array(nodes[0].embedding).flatten()
            all_embeddings.append(query_embedding)
            all_chunk_ids.append('QUERY')
            all_chunk_docs.append('QUERY')
            all_chunk_texts.append(nodes[0].text[:100] + '...' if len(nodes[0].text) > 100 else nodes[0].text)
            query_in_graph = True
            print(f"   📍 Added query to graph")

        # Add all KG chunks
        for chunk_id, chunk_obj in all_kg_chunks.items():
            embedding = self._get_chunk_embedding(chunk_id)
            if embedding is not None:
                # Ensure embedding is a 1D numpy array
                embedding = np.array(embedding).flatten()
                all_embeddings.append(embedding)
                all_chunk_ids.append(chunk_id)
                # Get document
                doc = self._get_chunk_document(chunk_id)
                all_chunk_docs.append(doc)
                # Get text preview
                text = chunk_obj.chunk_text if hasattr(chunk_obj, 'chunk_text') else ''
                all_chunk_texts.append(text[:100] + '...' if len(text) > 100 else text)

        if len(all_embeddings) < 2:
            print("⚠️ Not enough chunks in knowledge graph, falling back to traversal-only view")
            return self._create_3d_plot_traversal_only(nodes, result, query, method)

        print(f"   📊 Total chunks in KG: {len(all_embeddings)}")

        # Debug: Check embedding types
        embedding_types = set(type(emb).__name__ for emb in all_embeddings if emb is not None)
        print(f"   🔍 Embedding types found: {embedding_types}")

        # Verify all embeddings have the same dimension BEFORE converting to array
        # Check for None values first
        all_embeddings_clean = []
        all_chunk_ids_clean = []
        all_chunk_docs_clean = []
        all_chunk_texts_clean = []

        for i, emb in enumerate(all_embeddings):
            if emb is not None and isinstance(emb, np.ndarray) and emb.size > 0:
                all_embeddings_clean.append(emb)
                all_chunk_ids_clean.append(all_chunk_ids[i])
                all_chunk_docs_clean.append(all_chunk_docs[i])
                all_chunk_texts_clean.append(all_chunk_texts[i])
            else:
                print(f"   ⚠️ Skipping invalid embedding at index {i}: type={type(emb)}, chunk_id={all_chunk_ids[i] if i < len(all_chunk_ids) else 'unknown'}")

        print(f"   ✅ Kept {len(all_embeddings_clean)}/{len(all_embeddings)} valid embeddings")

        all_embeddings = all_embeddings_clean
        all_chunk_ids = all_chunk_ids_clean
        all_chunk_docs = all_chunk_docs_clean
        all_chunk_texts = all_chunk_texts_clean

        # Now check dimensions
        embedding_dims = [emb.shape[0] for emb in all_embeddings]
        unique_dims = set(embedding_dims)

        if len(unique_dims) > 1:
            # Filter to keep only the most common dimension
            from collections import Counter
            most_common_dim = Counter(embedding_dims).most_common(1)[0][0]
            print(f"⚠️ Found embeddings with inconsistent dimensions: {unique_dims}")
            print(f"   Keeping only embeddings with dimension {most_common_dim}")

            filtered_embeddings = []
            filtered_chunk_ids = []
            filtered_chunk_docs = []
            filtered_chunk_texts = []

            for i, emb in enumerate(all_embeddings):
                if emb.shape[0] == most_common_dim:
                    filtered_embeddings.append(emb)
                    filtered_chunk_ids.append(all_chunk_ids[i])
                    filtered_chunk_docs.append(all_chunk_docs[i])
                    filtered_chunk_texts.append(all_chunk_texts[i])

            all_embeddings = filtered_embeddings
            all_chunk_ids = filtered_chunk_ids
            all_chunk_docs = filtered_chunk_docs
            all_chunk_texts = filtered_chunk_texts

            print(f"   Kept {len(all_embeddings)} embeddings with dimension {most_common_dim}")

        # Now safely convert to numpy array
        embeddings_array = np.array(all_embeddings)
        embeddings_array = embeddings_array / np.linalg.norm(embeddings_array, axis=1, keepdims=True)

        # Apply dimensionality reduction to ALL chunks
        if method == "pca":
            reducer = PCA(n_components=3, random_state=42)
            coords_3d = reducer.fit_transform(embeddings_array)
            explained_variance = reducer.explained_variance_ratio_
            subtitle = f"PCA (explained variance: {explained_variance.sum():.1%})"
        else:  # t-SNE
            perplexity = min(30, len(embeddings_array) - 1)
            perplexity = max(5, perplexity)
            reducer = TSNE(n_components=3, random_state=42, perplexity=perplexity, n_iter=1000)
            coords_3d = reducer.fit_transform(embeddings_array)
            subtitle = "t-SNE"

        # Scale coordinates to spread out the visualization
        scale_factor = 6.0
        coords_3d = coords_3d * scale_factor

        print(f"🔬 Applied {method.upper()} dimensionality reduction to {len(embeddings_array)} embeddings")
        print(f"📏 Applied {scale_factor}x scaling for better spacing")

        # Create the figure
        fig = go.Figure()

        # STEP 1: Add graph structure edges (thin black/gray lines at configurable similarity threshold)
        print(f"🔗 Computing knowledge graph structure...")
        from sklearn.metrics.pairwise import cosine_similarity
        sim_matrix = cosine_similarity(embeddings_array)

        # Use configurable threshold (higher = fewer edges, less dense visualization)
        edge_pairs = []
        for i in range(len(all_embeddings)):
            for j in range(i+1, len(all_embeddings)):
                if sim_matrix[i, j] > edge_threshold:
                    edge_pairs.append((i, j))

        print(f"   ✅ Found {len(edge_pairs)} connections above {edge_threshold} threshold")

        # Add graph edges (thin gray/black lines like the demo)
        edge_x, edge_y, edge_z = [], [], []
        for src, dst in edge_pairs:
            edge_x.extend([coords_3d[src, 0], coords_3d[dst, 0], None])
            edge_y.extend([coords_3d[src, 1], coords_3d[dst, 1], None])
            edge_z.extend([coords_3d[src, 2], coords_3d[dst, 2], None])

        if edge_x:
            fig.add_trace(go.Scatter3d(
                x=edge_x, y=edge_y, z=edge_z,
                mode='lines',
                line=dict(color='rgba(0,0,0,0.15)', width=1),  # Black with low opacity - subtle but defined
                hoverinfo='none',
                showlegend=False,
                name='Graph Structure'
            ))

        # STEP 2: Add all KG nodes (colored by document, matching demo style)
        unique_docs = list(set(all_chunk_docs))
        # Remove QUERY from background nodes (it will be added separately later)
        unique_docs = [doc for doc in unique_docs if doc != 'QUERY']
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan']
        doc_color_map = {doc: colors[i % len(colors)] for i, doc in enumerate(unique_docs)}

        print(f"   📚 Documents in KG: {unique_docs}")

        # Add nodes grouped by document (matching demo density/visibility)
        for doc in unique_docs:
            doc_mask = [d == doc for d in all_chunk_docs]
            doc_coords = coords_3d[doc_mask]
            doc_texts = [all_chunk_texts[i] for i, mask in enumerate(doc_mask) if mask]

            fig.add_trace(go.Scatter3d(
                x=doc_coords[:, 0],
                y=doc_coords[:, 1],
                z=doc_coords[:, 2],
                mode='markers',
                marker=dict(
                    size=5,  # Slightly larger like demo
                    color=doc_color_map[doc],
                    line=dict(color='black', width=0.5),  # More visible border
                    opacity=1.0  # Full opacity like demo
                ),
                text=doc_texts,
                hovertemplate='<b>%{text}</b><extra></extra>',
                name=doc,  # Cleaner legend name
                showlegend=True
            ))

        # STEP 3: Highlight traversal path with thick black bold edges
        print(f"🎯 Highlighting traversal path...")
        traversal_chunk_ids = set()
        for node in nodes:
            if node.node_type == 'chunk':
                traversal_chunk_ids.add(node.node_id)

        # Create mapping from chunk_id to index in coords_3d
        chunk_id_to_idx = {chunk_id: i for i, chunk_id in enumerate(all_chunk_ids)}

        # Highlight traversed nodes
        traversal_indices = []
        traversal_texts = []
        traversal_steps = []

        for node in nodes:
            if node.node_type == 'chunk' and node.node_id in chunk_id_to_idx:
                idx = chunk_id_to_idx[node.node_id]
                traversal_indices.append(idx)
                traversal_texts.append(f"Step {node.step_number}: {node.text}")
                traversal_steps.append(node.step_number)

        if traversal_indices:
            traversal_coords = coords_3d[traversal_indices]

            # Separate query node from other traversal nodes
            query_node_idx = None
            if nodes and nodes[0].node_type == 'query':
                # Query is the first node in our arrays (index 0) if we added it
                if query_in_graph and 'QUERY' in all_chunk_ids:
                    query_node_idx = all_chunk_ids.index('QUERY')

            # Add query node separately with special styling
            if query_node_idx is not None and query_node_idx < len(coords_3d):
                fig.add_trace(go.Scatter3d(
                    x=[coords_3d[query_node_idx, 0]],
                    y=[coords_3d[query_node_idx, 1]],
                    z=[coords_3d[query_node_idx, 2]],
                    mode='markers+text',
                    marker=dict(
                        size=20,
                        color='gold',
                        symbol='diamond',
                        line=dict(color='black', width=3),
                        opacity=1.0
                    ),
                    text=['Q'],
                    textposition="middle center",
                    textfont=dict(size=14, color='black', family='Arial Black'),
                    hovertemplate=f'<b>QUERY</b><br>{nodes[0].text}<extra></extra>',
                    name='Query',
                    showlegend=True
                ))

            # Add traversal path nodes (larger and more visible)
            fig.add_trace(go.Scatter3d(
                x=traversal_coords[:, 0],
                y=traversal_coords[:, 1],
                z=traversal_coords[:, 2],
                mode='markers+text',
                marker=dict(
                    size=15,  # Larger nodes
                    color='gold',
                    line=dict(color='black', width=2.5),  # Thicker border
                    opacity=1.0
                ),
                text=[str(s) for s in traversal_steps],
                textposition="middle center",
                textfont=dict(size=11, color='black', family='Arial Black'),
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=traversal_texts,
                name='Traversal Path',
                showlegend=True
            ))

        # Add thick black traversal edges (very prominent)
        if len(nodes) > 1:
            step_ordered_nodes = [n for n in nodes if n.node_type == 'chunk' and n.node_id in chunk_id_to_idx]
            step_ordered_nodes.sort(key=lambda x: x.step_number)

            for i in range(len(step_ordered_nodes) - 1):
                current_node = step_ordered_nodes[i]
                next_node = step_ordered_nodes[i + 1]

                current_idx = chunk_id_to_idx[current_node.node_id]
                next_idx = chunk_id_to_idx[next_node.node_id]

                # Very thick black edges for traversal path (more prominent than graph edges)
                fig.add_trace(go.Scatter3d(
                    x=[coords_3d[current_idx, 0], coords_3d[next_idx, 0]],
                    y=[coords_3d[current_idx, 1], coords_3d[next_idx, 1]],
                    z=[coords_3d[current_idx, 2], coords_3d[next_idx, 2]],
                    mode='lines',
                    line=dict(color='black', width=8),  # Even thicker
                    hovertemplate=f"Step {current_node.step_number} → {next_node.step_number}<extra></extra>",
                    showlegend=False,
                    name='Traversal Edge'
                ))

        # Update layout
        fig.update_layout(
            title=f"{result.algorithm_name} - Full Knowledge Graph with Traversal Path<br>" +
                  f"Query: '{query[:80]}...'<br>" +
                  f"KG: {len(all_embeddings)} chunks, {len(edge_pairs)} connections | " +
                  f"Traversal: {len(traversal_indices)} steps | " +
                  f"Score: {result.final_score:.3f}<br>" +
                  f"<i>{subtitle}</i>",
            scene=dict(
                xaxis_title=f"PC1" if method == "pca" else "Dim 1",
                yaxis_title=f"PC2" if method == "pca" else "Dim 2",
                zaxis_title=f"PC3" if method == "pca" else "Dim 3",
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
                bgcolor='rgba(240,240,240,0.9)'
            ),
            height=900,
            font=dict(size=12),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='gray',
                borderwidth=1
            ),
            margin=dict(l=0, r=0, t=150, b=0)
        )

        print(f"✅ Full knowledge graph visualization created successfully")
        return fig

    def _group_nodes_for_visualization(self, nodes: List[VisualizationNode], 
                                     coords_3d: np.ndarray) -> Dict[str, Dict]:
        """Group nodes for different visual treatment"""
        groups = {
            'query': {'nodes': [], 'coords': [], 'colors': [], 'sizes': [], 'symbols': []},
            'final_sentences': {'nodes': [], 'coords': [], 'colors': [], 'sizes': [], 'symbols': []},
            'final_chunks': {'nodes': [], 'coords': [], 'colors': [], 'sizes': [], 'symbols': []},
            'traversal_sentences': {'nodes': [], 'coords': [], 'colors': [], 'sizes': [], 'symbols': []},
            'traversal_chunks': {'nodes': [], 'coords': [], 'colors': [], 'sizes': [], 'symbols': []}
        }

        for i, node in enumerate(nodes):
            coord = coords_3d[i]
            
            if node.node_type == 'query':
                groups['query']['nodes'].append(node)
                groups['query']['coords'].append(coord)
                groups['query']['colors'].append('gold')
                groups['query']['sizes'].append(25)
                groups['query']['symbols'].append('diamond')  # Using diamond instead of star
            elif node.is_final_result:
                if node.node_type == 'sentence':
                    groups['final_sentences']['nodes'].append(node)
                    groups['final_sentences']['coords'].append(coord)
                    groups['final_sentences']['colors'].append('darkgreen')
                    groups['final_sentences']['sizes'].append(15 + node.relevance_score * 10)
                    groups['final_sentences']['symbols'].append('circle')
                else:
                    groups['final_chunks']['nodes'].append(node)
                    groups['final_chunks']['coords'].append(coord)
                    groups['final_chunks']['colors'].append('green')
                    groups['final_chunks']['sizes'].append(12 + node.relevance_score * 8)
                    groups['final_chunks']['symbols'].append('square')
            else:
                # Traversal nodes
                if node.node_type == 'sentence':
                    groups['traversal_sentences']['nodes'].append(node)
                    groups['traversal_sentences']['coords'].append(coord)
                    # Color based on relevance score
                    intensity = 0.3 + (node.relevance_score * 0.7)
                    color = f'rgba(0, {int(255 * intensity)}, 0, 0.6)'
                    groups['traversal_sentences']['colors'].append(color)
                    groups['traversal_sentences']['sizes'].append(8 + node.relevance_score * 6)
                    groups['traversal_sentences']['symbols'].append('circle')
                else:
                    groups['traversal_chunks']['nodes'].append(node)
                    groups['traversal_chunks']['coords'].append(coord)
                    groups['traversal_chunks']['colors'].append('lightblue')
                    groups['traversal_chunks']['sizes'].append(6 + node.relevance_score * 4)
                    groups['traversal_chunks']['symbols'].append('square')

        return groups

    def _add_node_group_trace(self, fig: go.Figure, group_name: str, group_data: Dict):
        """Add a trace for a group of nodes"""
        nodes = group_data['nodes']
        coords = np.array(group_data['coords'])
        colors = group_data['colors']
        sizes = group_data['sizes']
        symbols = group_data['symbols']

        if len(nodes) == 0:
            return

        # Create hover text
        hover_texts = []
        for node in nodes:
            hover_text = (
                f"<b>{group_name.replace('_', ' ').title()}</b><br>" +
                f"Step: {node.step_number}<br>" +
                f"Relevance: {node.relevance_score:.3f}<br>" +
                f"Connection: {node.connection_type}<br>" +
                f"Document: {node.document_id}<br>" +
                f"Text: {node.text[:150]}..."
            )
            hover_texts.append(hover_text)

        # Create step number labels for display
        step_labels = [str(node.step_number) if node.step_number >= 0 else 'Q' for node in nodes]

        # Determine marker properties
        if group_name == 'query':
            marker_symbol = 'diamond'  # Using diamond instead of star (star not supported)
            show_text = True
        else:
            marker_symbol = 'circle' if 'sentence' in group_name else 'square'
            show_text = True

        # Add trace
        trace = go.Scatter3d(
            x=coords[:, 0],
            y=coords[:, 1],
            z=coords[:, 2],
            mode='markers+text' if show_text else 'markers',
            marker=dict(
                size=sizes,
                color=colors,
                symbol=marker_symbol,
                line=dict(width=2, color='black' if group_name == 'query' else 'gray'),
                opacity=1.0 if 'final' in group_name or group_name == 'query' else 0.7
            ),
            text=step_labels if show_text else None,
            textposition="middle center",
            textfont=dict(size=10, color='black'),
            name=group_name.replace('_', ' ').title(),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hover_texts
        )

        fig.add_trace(trace)

    def _add_traversal_path_lines(self, fig: go.Figure, nodes: List[VisualizationNode],
                                  coords_3d: np.ndarray, result: RetrievalResult):
        """Add lines showing the traversal path (like reference examples)"""

        if result.algorithm_name == "BasicRetrieval":
            # For BasicRetrieval, connect query to all final results
            query_indices = [i for i, node in enumerate(nodes) if node.node_type == "query"]
            final_result_indices = [i for i, node in enumerate(nodes) if node.is_final_result]

            if query_indices:
                query_idx = query_indices[0]
                for final_idx in final_result_indices:
                    fig.add_trace(go.Scatter3d(
                        x=[coords_3d[query_idx, 0], coords_3d[final_idx, 0]],
                        y=[coords_3d[query_idx, 1], coords_3d[final_idx, 1]],
                        z=[coords_3d[query_idx, 2], coords_3d[final_idx, 2]],
                        mode='lines',
                        line=dict(color='orange', width=3, dash='dot'),
                        showlegend=False,
                        hovertemplate="Query → Final Result<extra></extra>",
                        name="Connection"
                    ))
        else:
            # For traversal algorithms, connect nodes in step order
            step_ordered_nodes = [(i, node) for i, node in enumerate(nodes) 
                                if node.step_number >= 0 and node.node_type != 'query']
            step_ordered_nodes.sort(key=lambda x: x[1].step_number)

            for i in range(len(step_ordered_nodes) - 1):
                current_idx, current_node = step_ordered_nodes[i]
                next_idx, next_node = step_ordered_nodes[i + 1]

                # Color based on connection type (like reference examples)
                if next_node.connection_type in ['cross_document', 'theme_bridge']:
                    line_color = 'red'
                    line_width = 4
                    line_dash = 'solid'
                elif next_node.connection_type == 'hierarchical':
                    line_color = 'purple'
                    line_width = 3
                    line_dash = 'dash'
                else:
                    line_color = 'blue'
                    line_width = 2
                    line_dash = 'dot'

                fig.add_trace(go.Scatter3d(
                    x=[coords_3d[current_idx, 0], coords_3d[next_idx, 0]],
                    y=[coords_3d[current_idx, 1], coords_3d[next_idx, 1]],
                    z=[coords_3d[current_idx, 2], coords_3d[next_idx, 2]],
                    mode='lines',
                    line=dict(color=line_color, width=line_width, dash=line_dash),
                    showlegend=False,
                    hovertemplate=f"Step {current_node.step_number} → {next_node.step_number}<br>" +
                                  f"Connection: {next_node.connection_type}<extra></extra>",
                    name="Traversal Path"
                ))

    def _create_basic_plotly_visualization(self, result: RetrievalResult, query: str) -> go.Figure:
        """Create a basic visualization when 3D plot is not possible"""
        fig = go.Figure()

        # Create a simple text display
        fig.add_annotation(
            text=f"<b>{result.algorithm_name} Results</b><br><br>" +
                 f"Query: {query[:100]}...<br>" +
                 f"Retrieved Sentences: {len(result.retrieved_content)}<br>" +
                 f"Final Score: {result.final_score:.3f}<br>" +
                 f"Processing Time: {result.processing_time:.3f}s",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16),
            align="center"
        )

        fig.update_layout(
            title=f"{result.algorithm_name} - Basic Visualization",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=600
        )

        return fig

    # Utility methods for data extraction
    def _get_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """Get embedding for the query using available methods"""
        # Try to use the knowledge graph's encoding method if available
        if hasattr(self.kg, 'encode_query'):
            return self.kg.encode_query(query)
        elif hasattr(self.kg, 'embedding_model'):
            return self.kg.embedding_model.encode([query])[0]
        else:
            # Fallback: use cached model to avoid repeated loading
            return self._encode_text(query)

    def _encode_text(self, text: str) -> np.ndarray:
        """Fallback text encoding method using KG's model if available"""
        try:
            # Try to use the knowledge graph's existing model first
            if hasattr(self.kg, 'embedding_model'):
                return self.kg.embedding_model.encode([text])[0]
            else:
                # Fallback: create model once and reuse (use CURRENT model, not old one!)
                if not hasattr(self, '_fallback_model'):
                    from sentence_transformers import SentenceTransformer
                    self._fallback_model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1')
                return self._fallback_model.encode([text])[0]
        except Exception as e:
            print(f"⚠️ Warning: Could not encode text '{text[:50]}...': {e}")
            # Return a dummy embedding if all else fails
            return np.random.normal(0, 1, 1024)  # Updated dimension to 1024 for mxbai

    def _get_sentence_embedding(self, sentence_id: str) -> Optional[np.ndarray]:
        """Get cached embedding for a sentence"""
        sentence_obj = self.kg.sentences.get(sentence_id)
        if sentence_obj:
            for attr in ['embedding', 'embeddings', 'vector']:
                if hasattr(sentence_obj, attr):
                    embedding = getattr(sentence_obj, attr)
                    if embedding is not None:
                        return np.array(embedding)
        return None

    def _get_chunk_embedding(self, chunk_id: str) -> Optional[np.ndarray]:
        """Get cached embedding for a chunk"""
        # Use knowledge graph's built-in method first (it has the embedding cache!)
        if hasattr(self.kg, 'get_chunk_embedding'):
            embedding = self.kg.get_chunk_embedding(chunk_id)
            if embedding is not None:
                return np.array(embedding)

        # Fallback: try to get from chunk object attributes
        chunk_obj = self.kg.chunks.get(chunk_id)
        if chunk_obj:
            for attr in ['embedding', 'embeddings', 'vector']:
                if hasattr(chunk_obj, attr):
                    embedding = getattr(chunk_obj, attr)
                    if embedding is not None:
                        return np.array(embedding)
        return None

    def _find_sentence_id(self, sentence_text: str) -> Optional[str]:
        """Find sentence ID by text content"""
        for sentence_id, sentence_obj in self.kg.sentences.items():
            if hasattr(sentence_obj, 'sentence_text') and sentence_obj.sentence_text == sentence_text:
                return sentence_id
        return None

    def _get_sentence_document(self, sentence_obj) -> str:
        """Get document ID for a sentence object"""
        for attr in ['source_document', 'document_id', 'doc_id']:
            if hasattr(sentence_obj, attr):
                doc_id = getattr(sentence_obj, attr)
                if doc_id:
                    return str(doc_id)
        return "unknown"

    def _get_chunk_document(self, chunk_id: str) -> str:
        """Get document ID for a chunk"""
        chunk_obj = self.kg.chunks.get(chunk_id)
        if chunk_obj:
            for attr in ['source_document', 'document_id', 'doc_id']:
                if hasattr(chunk_obj, attr):
                    doc_id = getattr(chunk_obj, attr)
                    if doc_id:
                        return str(doc_id)
        
        # Fallback: extract from chunk ID
        if '_' in chunk_id:
            parts = chunk_id.split('_')
            if len(parts) >= 2:
                return '_'.join(parts[:-1])
            return parts[0]
        
        return "unknown"

    def _calculate_node_relevance(self, node_id: str, result: RetrievalResult) -> float:
        """Calculate relevance score for a node"""
        # Try query similarities first
        if hasattr(result, 'query_similarities') and result.query_similarities:
            if node_id in result.query_similarities:
                return result.query_similarities[node_id]

            # For chunks, find max similarity among sentences
            if hasattr(self.kg, 'get_chunk_sentences'):
                chunk_sentences = self.kg.get_chunk_sentences(node_id)
                if chunk_sentences:
                    max_similarity = 0.0
                    for sentence in chunk_sentences:
                        sentence_text = sentence.sentence_text if hasattr(sentence, 'sentence_text') else str(sentence)
                        similarity = result.query_similarities.get(sentence_text, 0.0)
                        max_similarity = max(max_similarity, similarity)
                    return max_similarity

        # Try metadata
        if hasattr(result, 'metadata') and result.metadata:
            extraction_metadata = result.metadata.get('extraction_metadata', {})
            if node_id in extraction_metadata:
                return extraction_metadata[node_id].get('similarity_score', 0.5)

        return 0.5  # Default

    def _get_all_kg_chunks(self) -> Dict:
        """Get all chunks from the knowledge graph"""
        return self.kg.chunks

    def _create_3d_plot_traversal_only(self, nodes: List[VisualizationNode], result: RetrievalResult,
                                      query: str, method: str) -> go.Figure:
        """Fallback method that creates visualization with only traversal nodes (old behavior)"""
        # Get embeddings and reduce dimensionality
        embeddings = np.array([node.embedding for node in nodes])
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        if method == "pca":
            reducer = PCA(n_components=3, random_state=42)
            coords_3d = reducer.fit_transform(embeddings)
            explained_variance = reducer.explained_variance_ratio_
            subtitle = f"PCA (explained variance: {explained_variance.sum():.1%})"
        else:  # t-SNE
            perplexity = min(30, len(embeddings) - 1)
            perplexity = max(5, perplexity)
            reducer = TSNE(n_components=3, random_state=42, perplexity=perplexity, n_iter=1000)
            coords_3d = reducer.fit_transform(embeddings)
            subtitle = "t-SNE"

        fig = go.Figure()

        # Group nodes by type and status
        node_groups = self._group_nodes_for_visualization(nodes, coords_3d)

        # Plot each group
        for group_name, group_data in node_groups.items():
            if not group_data['nodes']:
                continue
            self._add_node_group_trace(fig, group_name, group_data)

        # Add traversal path lines
        self._add_traversal_path_lines(fig, nodes, coords_3d, result)

        # Update layout
        fig.update_layout(
            title=f"{result.algorithm_name} Semantic Traversal Visualization<br>" +
                  f"Query: '{query[:80]}...'<br>" +
                  f"Retrieved: {len(result.retrieved_content)} sentences | " +
                  f"Traversed: {len(nodes)} nodes | " +
                  f"Score: {result.final_score:.3f}<br>" +
                  f"<i>{subtitle}</i>",
            scene=dict(
                xaxis_title=f"Dimension 1 ({method.upper()})",
                yaxis_title=f"Dimension 2 ({method.upper()})",
                zaxis_title=f"Dimension 3 ({method.upper()})",
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
                bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showspikes=False, showgrid=True, gridcolor='lightgray'),
                yaxis=dict(showspikes=False, showgrid=True, gridcolor='lightgray'),
                zaxis=dict(showspikes=False, showgrid=True, gridcolor='lightgray')
            ),
            height=900,
            font=dict(size=12),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='gray',
                borderwidth=1
            ),
            margin=dict(l=0, r=0, t=150, b=0)
        )

        return fig


def create_algorithm_visualization(result: RetrievalResult, query: str,
                                   knowledge_graph: KnowledgeGraph,
                                   method: str = "pca", max_nodes: int = 50,
                                   show_all_visited: bool = True,
                                   edge_threshold: float = 0.75) -> go.Figure:
    """
    Main entry point for creating 3D visualizations of algorithm results.
    Matches the style and functionality of the perfect reference examples.

    Args:
        result: RetrievalResult from any algorithm
        query: Original query string
        knowledge_graph: The knowledge graph instance
        method: Dimensionality reduction method ('pca' or 'tsne')
        max_nodes: Maximum nodes to show for performance
        show_all_visited: Whether to show all visited nodes or just final results
        edge_threshold: Similarity threshold for showing edges (0.0-1.0, higher = fewer edges)
                       Default 0.75. Try 0.8-0.85 for less dense visualizations.

    Returns:
        Plotly Figure ready for display or saving
    """
    visualizer = KnowledgeGraphPlotlyVisualizer(knowledge_graph)
    return visualizer.visualize_retrieval_result(
        result, query, method, max_nodes, show_all_visited, edge_threshold
    )


# Example usage function
def example_usage():
    """Example of how to use the visualizer"""

    print("Example usage:")
    print("from utils.plotly_visualizer import create_algorithm_visualization")
    print("")
    print("# After running an algorithm:")
    print("result = retrieval_orchestrator.retrieve(query, 'query_traversal')")
    print("fig = create_algorithm_visualization(")
    print("    result=result,")
    print("    query=query,")
    print("    knowledge_graph=kg,")
    print("    method='pca',  # or 'tsne'")
    print("    max_nodes=50,")
    print("    show_all_visited=True")
    print(")")
    print("fig.show()  # Display interactive plot")
    print("# fig.write_html('visualization.html')  # Save to file")


def save_figure_for_a4_print(fig: go.Figure, output_path: str,
                            orientation: str = "portrait",
                            title: str = "Knowledge Graph Visualization",
                            description: str = "") -> str:
    """
    Save Plotly figure optimized for A4 printing.

    Args:
        fig: Plotly figure object
        output_path: Path to save the HTML file
        orientation: 'portrait' (纵向) or 'landscape' (横向)
        title: Page title
        description: Optional description text to include

    Returns:
        Path to the saved HTML file

    A4 sizes:
        Portrait: 210mm x 297mm (usable: ~700px x 1030px at 96 DPI)
        Landscape: 297mm x 210mm (usable: ~1030px x 700px at 96 DPI)
    """
    import os
    from pathlib import Path

    # Calculate optimal figure size for A4
    if orientation.lower() == "portrait":
        # A4 纵向 - 考虑页边距后的可用空间
        width = 700   # 约 185mm
        height = 850  # 约 225mm (留出标题和页脚空间)
        page_class = "page"
    else:  # landscape
        # A4 横向
        width = 1000  # 约 265mm
        height = 600  # 约 159mm
        page_class = "page landscape"

    # Update figure layout for print
    fig.update_layout(
        width=width,
        height=height,
        margin=dict(l=50, r=50, t=100, b=50),  # 适当的边距
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(size=10)  # 打印友好的字体大小
    )

    # Get figure HTML
    fig_html = fig.to_html(
        include_plotlyjs='cdn',
        div_id='main-chart',
        config={
            'displayModeBar': False,  # 打印时隐藏工具栏
            'staticPlot': False,       # 保持交互性（屏幕查看时）
            'responsive': True
        }
    )

    # Extract just the div part
    import re
    div_match = re.search(r'(<div id="main-chart".*?</script>)', fig_html, re.DOTALL)
    if div_match:
        chart_div = div_match.group(1)
    else:
        chart_div = fig_html

    # Build page content
    description_html = ""
    if description:
        description_html = f'<div class="chart-description">{description}</div>'

    page_content = f'''
    <div class="{page_class}">
        <div class="page-header">
            <h1>{title}</h1>
            <div class="subtitle">Knowledge Graph Traversal Visualization</div>
        </div>

        {description_html}

        <div class="chart-container">
            {chart_div}
        </div>

        <div class="page-footer">
            Page 1 | Generated with Plotly
        </div>
    </div>
    '''

    # Load template
    template_path = Path(__file__).parent / "plotly_a4_print_template.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    else:
        # Fallback template if file doesn't exist
        template = get_default_a4_template()

    # Replace placeholders
    html_content = template.replace('{{title}}', title)
    html_content = html_content.replace('{{content}}', page_content)

    # Save to file
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ A4 print-optimized HTML saved to: {output_path}")
    print(f"   Orientation: {orientation}")
    print(f"   Figure size: {width}x{height}px")
    print(f"   Open in browser and use Print (Ctrl+P) to save as PDF")

    return str(output_path)


def save_multiple_figures_for_a4_print(figures: List[Tuple[go.Figure, str, str]],
                                       output_path: str,
                                       orientation: str = "portrait",
                                       main_title: str = "Knowledge Graph Analysis Report") -> str:
    """
    Save multiple Plotly figures as a multi-page A4 document.

    Args:
        figures: List of (figure, title, description) tuples
        output_path: Path to save the HTML file
        orientation: 'portrait' or 'landscape'
        main_title: Overall document title

    Returns:
        Path to the saved HTML file
    """
    from pathlib import Path

    # Calculate optimal figure size
    if orientation.lower() == "portrait":
        width, height = 700, 850
        page_class = "page"
    else:
        width, height = 1000, 600
        page_class = "page landscape"

    pages_html = []

    for idx, (fig, title, description) in enumerate(figures, 1):
        # Update figure layout
        fig.update_layout(
            width=width,
            height=height,
            margin=dict(l=50, r=50, t=100, b=50),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(size=10)
        )

        # Get figure HTML
        fig_html = fig.to_html(
            include_plotlyjs='cdn' if idx == 1 else False,  # Only include Plotly.js once
            div_id=f'chart-{idx}',
            config={'displayModeBar': False, 'staticPlot': False, 'responsive': True}
        )

        # Extract div
        import re
        div_match = re.search(rf'(<div id="chart-{idx}".*?</script>)', fig_html, re.DOTALL)
        chart_div = div_match.group(1) if div_match else fig_html

        # Build description
        desc_html = f'<div class="chart-description">{description}</div>' if description else ''

        # Build page
        page_html = f'''
    <div class="{page_class}">
        <div class="page-header">
            <h1>{title}</h1>
            <div class="subtitle">{main_title}</div>
        </div>

        {desc_html}

        <div class="chart-container">
            {chart_div}
        </div>

        <div class="page-footer">
            Page {idx} of {len(figures)} | Generated with Plotly
        </div>
    </div>
        '''
        pages_html.append(page_html)

    # Load template
    template_path = Path(__file__).parent / "plotly_a4_print_template.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    else:
        template = get_default_a4_template()

    # Combine all pages
    all_pages = '\n'.join(pages_html)
    html_content = template.replace('{{title}}', main_title)
    html_content = html_content.replace('{{content}}', all_pages)

    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Multi-page A4 print-optimized HTML saved to: {output_path}")
    print(f"   Pages: {len(figures)}")
    print(f"   Orientation: {orientation}")

    return str(output_path)


def figure_to_base64(fig: go.Figure, width: int = 1200, height: int = 800,
                     scale: int = 2, format: str = 'png') -> str:
    """
    Convert Plotly figure to base64 encoded image.

    Args:
        fig: Plotly figure object
        width: Image width in pixels
        height: Image height in pixels
        scale: Scale factor for higher resolution (default 2 for retina displays)
        format: Image format ('png', 'jpeg', 'webp', 'svg')

    Returns:
        Base64 encoded string of the image

    Note:
        Requires kaleido: pip install kaleido
    """
    import base64
    from io import BytesIO

    try:
        # Try using kaleido (recommended)
        img_bytes = fig.to_image(
            format=format,
            width=width,
            height=height,
            scale=scale
        )
    except Exception as e:
        print(f"⚠️ Warning: kaleido not available ({e})")
        print("   Installing kaleido: pip install kaleido")
        print("   Falling back to plotly.io.to_image")

        try:
            import plotly.io as pio
            img_bytes = pio.to_image(
                fig,
                format=format,
                width=width,
                height=height,
                scale=scale
            )
        except Exception as e2:
            raise RuntimeError(
                f"Failed to convert figure to image. "
                f"Please install kaleido: pip install kaleido\n"
                f"Error: {e2}"
            )

    # Convert to base64
    base64_str = base64.b64encode(img_bytes).decode('utf-8')
    return base64_str


def save_figure_for_a4_print_static(fig: go.Figure, output_path: str,
                                   orientation: str = "portrait",
                                   title: str = "Knowledge Graph Visualization",
                                   description: str = "",
                                   image_quality: int = 2) -> str:
    """
    Save Plotly figure as static image (base64) optimized for A4 printing using Jinja2.

    This version converts Plotly charts to static PNG images embedded as base64,
    resulting in faster loading and more stable printing.

    Args:
        fig: Plotly figure object
        output_path: Path to save the HTML file
        orientation: 'portrait' (纵向) or 'landscape' (横向)
        title: Page title
        description: Optional description text
        image_quality: Scale factor for image resolution (1-4, higher = better quality)

    Returns:
        Path to the saved HTML file

    Requires:
        - jinja2: pip install jinja2
        - kaleido: pip install kaleido
    """
    from pathlib import Path

    try:
        from jinja2 import Template
    except ImportError:
        raise ImportError("Jinja2 not installed. Run: pip install jinja2")

    # Calculate optimal image size for A4
    if orientation.lower() == "portrait":
        # A4 纵向
        width = 700
        height = 850
    else:  # landscape
        # A4 横向
        width = 1000
        height = 600

    # Update figure layout for print
    fig.update_layout(
        width=width,
        height=height,
        margin=dict(l=50, r=50, t=80, b=50),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(size=11)
    )

    # Convert figure to base64
    print(f"📸 Converting figure to static image ({width}x{height}px, scale={image_quality})...")
    image_base64 = figure_to_base64(fig, width=width, height=height, scale=image_quality)
    print(f"   ✅ Image size: {len(image_base64) / 1024:.1f} KB")

    # Load Jinja2 template
    template_path = Path(__file__).parent / "plotly_a4_jinja2_template.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    else:
        # Fallback inline template
        template_content = get_jinja2_inline_template()

    template = Template(template_content)

    # Prepare data for template
    pages = [{
        'title': title,
        'subtitle': 'Knowledge Graph Traversal Visualization',
        'description': description,
        'image_base64': image_base64
    }]

    # Render HTML
    html_content = template.render(
        title=title,
        orientation=orientation,
        pages=pages
    )

    # Save to file
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ A4 static image HTML saved to: {output_path}")
    print(f"   Orientation: {orientation}")
    print(f"   Image size: {width}x{height}px (scale {image_quality}x)")
    print(f"   File is self-contained with embedded base64 image")
    print(f"   Open in browser and use Print (Ctrl+P) to save as PDF")

    return str(output_path)


def save_multiple_figures_for_a4_print_static(
    figures: List[Tuple[go.Figure, str, str]],
    output_path: str,
    orientation: str = "portrait",
    main_title: str = "Knowledge Graph Analysis Report",
    image_quality: int = 2
) -> str:
    """
    Save multiple Plotly figures as static images in a multi-page A4 document using Jinja2.

    Args:
        figures: List of (figure, title, description) tuples
        output_path: Path to save the HTML file
        orientation: 'portrait' or 'landscape'
        main_title: Overall document title
        image_quality: Scale factor for image resolution (1-4)

    Returns:
        Path to the saved HTML file

    Requires:
        - jinja2: pip install jinja2
        - kaleido: pip install kaleido
    """
    from pathlib import Path

    try:
        from jinja2 import Template
    except ImportError:
        raise ImportError("Jinja2 not installed. Run: pip install jinja2")

    # Calculate optimal image size
    if orientation.lower() == "portrait":
        width, height = 700, 850
    else:
        width, height = 1000, 600

    pages = []

    for idx, (fig, title, description) in enumerate(figures, 1):
        print(f"📸 Processing figure {idx}/{len(figures)}: {title}")

        # Update figure layout
        fig.update_layout(
            width=width,
            height=height,
            margin=dict(l=50, r=50, t=80, b=50),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(size=11)
        )

        # Convert to base64
        image_base64 = figure_to_base64(fig, width=width, height=height, scale=image_quality)
        print(f"   ✅ Image {idx} size: {len(image_base64) / 1024:.1f} KB")

        pages.append({
            'title': title,
            'subtitle': main_title,
            'description': description,
            'image_base64': image_base64
        })

    # Load template
    template_path = Path(__file__).parent / "plotly_a4_jinja2_template.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    else:
        template_content = get_jinja2_inline_template()

    template = Template(template_content)

    # Render HTML
    html_content = template.render(
        title=main_title,
        orientation=orientation,
        pages=pages
    )

    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    total_size = sum(len(p['image_base64']) for p in pages) / 1024
    print(f"\n✅ Multi-page static HTML saved to: {output_path}")
    print(f"   Pages: {len(figures)}")
    print(f"   Orientation: {orientation}")
    print(f"   Total embedded image size: {total_size:.1f} KB")
    print(f"   File is self-contained and ready for printing")

    return str(output_path)


def get_jinja2_inline_template() -> str:
    """Inline Jinja2 template as fallback"""
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, "Microsoft YaHei", sans-serif; background: #f5f5f5; padding: 20px; }
        .page { background: white; margin: 0 auto 20px; padding: 20mm; box-shadow: 0 0 10px rgba(0,0,0,0.1); position: relative; }
        .page.portrait { width: 210mm; min-height: 297mm; }
        .page.landscape { width: 297mm; min-height: 210mm; }
        .page-header { text-align: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #333; }
        .page-header h1 { font-size: 24px; margin-bottom: 5px; }
        .page-header .subtitle { font-size: 14px; color: #666; }
        .page-footer { position: absolute; bottom: 15mm; left: 20mm; right: 20mm; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #ddd; padding-top: 5px; }
        .chart-container { width: 100%; text-align: center; margin: 10px 0; page-break-inside: avoid; }
        .chart-container img { max-width: 100%; height: auto; display: block; margin: 0 auto; }
        .chart-description { margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #4CAF50; font-size: 14px; }
        .print-button { position: fixed; top: 20px; right: 20px; padding: 12px 24px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; z-index: 1000; }
        .print-button:hover { background: #45a049; }
        @media print {
            body { background: white; padding: 0; }
            .page { margin: 0; padding: 20mm; box-shadow: none; page-break-after: always; }
            .page.portrait { width: 210mm; height: 297mm; }
            .page.landscape { width: 297mm; height: 210mm; }
            .page:last-child { page-break-after: auto; }
            .chart-container { page-break-inside: avoid; }
            .print-button { display: none !important; }
        }
        @page { size: A4 {{ 'landscape' if orientation == 'landscape' else 'portrait' }}; margin: 0; }
    </style>
</head>
<body>
    <button class="print-button" onclick="window.print()">🖨️ 打印 / 保存为PDF</button>
    {% for page in pages %}
    <div class="page {{ orientation }}">
        <div class="page-header">
            <h1>{{ page.title }}</h1>
            {% if page.subtitle %}<div class="subtitle">{{ page.subtitle }}</div>{% endif %}
        </div>
        {% if page.description %}<div class="chart-description">{{ page.description }}</div>{% endif %}
        <div class="chart-container">
            <img src="data:image/png;base64,{{ page.image_base64 }}" alt="{{ page.title }}">
        </div>
        <div class="page-footer">Page {{ loop.index }}{% if pages|length > 1 %} of {{ pages|length }}{% endif %} | Generated with Plotly</div>
    </div>
    {% endfor %}
</body>
</html>"""


def get_default_a4_template() -> str:
    """Fallback template if template file is not found"""
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{{title}}</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }
.page { background: white; margin: 0 auto 20px; padding: 20mm; width: 210mm; min-height: 297mm; box-shadow: 0 0 10px rgba(0,0,0,0.1); position: relative; }
.page.landscape { width: 297mm; min-height: 210mm; }
.page-header { text-align: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #333; }
.page-header h1 { font-size: 24px; margin-bottom: 5px; }
.page-footer { position: absolute; bottom: 15mm; left: 20mm; right: 20mm; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #ddd; padding-top: 5px; }
.chart-container { width: 100%; margin: 10px 0; }
.chart-description { margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #4CAF50; }
.print-button { position: fixed; top: 20px; right: 20px; padding: 12px 24px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; z-index: 1000; }
@media print {
    body { background: white; padding: 0; }
    .page { margin: 0; padding: 20mm; box-shadow: none; page-break-after: always; width: 210mm; height: 297mm; }
    .page.landscape { width: 297mm; height: 210mm; }
    .page:last-child { page-break-after: auto; }
    .chart-container { page-break-inside: avoid; }
    .print-button, .no-print { display: none !important; }
}
@page { size: A4 portrait; margin: 0; }
</style></head><body>
<button class="print-button" onclick="window.print()">🖨️ 打印 / 保存为PDF</button>
{{content}}
</body></html>"""


if __name__ == "__main__":
    example_usage()
