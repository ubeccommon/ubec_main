# holonic/ubec_holonic_visualizer.py

import os
import sys
import logging
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import networkx as nx
from io import BytesIO
import base64

# Import database utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.connection import DatabaseManager

class UBECHolonicVisualizer:
    """
    Visualizes UBEC holonic evaluation results from database or report file.
    """
    
    def __init__(self, report_file=None, db_connection=None):
        """
        Initialize the holonic visualizer.
        
        Args:
            report_file: Path to evaluation report JSON file (optional)
            db_connection: Optional database connection to use
        """
        # Create DatabaseManager instance
        self.db_conn = db_connection or DatabaseManager(schema=os.getenv('UBEC_DB_SCHEMA', 'ubec_main'))
        self.report_data = None
        self.transaction_network = None
        
        # Load data from database by default, unless report_file is provided
        if report_file:
            self.load_report(report_file)
        else:
            self.load_evaluation_data_from_db()
    
    def load_report(self, report_file):
        """
        Load evaluation report from file.
        
        Args:
            report_file: Path to evaluation report JSON file
        """
        try:
            with open(report_file, 'r') as f:
                self.report_data = json.load(f)
            logging.info(f"Loaded evaluation report from {report_file}")
        except Exception as e:
            logging.error(f"Error loading report file: {e}")
    
    def load_evaluation_data_from_db(self, limit=500):
        """
        Load evaluation data from database.
        
        Args:
            limit: Maximum number of evaluation records to load
            
        Returns:
            Dict with evaluation data
        """
        try:
            # Get most recent evaluation data
            query = """
            WITH latest_evals AS (
                SELECT DISTINCT ON (agent_id) *
                FROM ubec_main.holonic_metrics
                ORDER BY agent_id, evaluation_date DESC
            )
            SELECT hm.agent_id, a.agent_id AS public_key, p.account_id,
                   hm.evaluation_date, hm.autonomy_integration_score,
                   hm.multi_scale_score, hm.regenerative_impact_score,
                   hm.network_contribution_score, hm.ubuntu_alignment_score,
                   hm.composite_score, hm.holonic_category, hm.raw_metrics
            FROM latest_evals hm
            JOIN ubec_main.agents a ON hm.agent_id = a.id
            JOIN ubec_main.participants p ON a.participant_id = p.id
            ORDER BY hm.composite_score DESC
            LIMIT %s
            """
            
            # Use DatabaseManager's execute_query method instead
            results = self.db_conn.execute_query(query, [limit], fetch_all=True)
            
            if not results or len(results) == 0:
                logging.warning("No evaluation data found in database")
                # Create empty report structure for consistency
                self.report_data = {
                    "status": "success",
                    "evaluated_count": 0,
                    "evaluation_date": datetime.now().isoformat(),
                    "category_distribution": {},
                    "average_scores": {
                        'autonomy': 0, 
                        'multi_scale': 0, 
                        'regenerative': 0,
                        'network': 0, 
                        'ubuntu': 0, 
                        'composite': 0
                    },
                    "results": []
                }
                return self.report_data
            
            # Get category distribution
            query = """
            WITH latest_evals AS (
                SELECT DISTINCT ON (agent_id) *
                FROM ubec_main.holonic_metrics
                ORDER BY agent_id, evaluation_date DESC
            )
            SELECT holonic_category, COUNT(*) as count
            FROM latest_evals
            GROUP BY holonic_category
            """
            
            # Use DatabaseManager's execute_query method
            categories = self.db_conn.execute_query(query, fetch_all=True)
            category_distribution = {cat['holonic_category']: cat['count'] for cat in categories} if categories else {}
            
            # Calculate average scores
            query = """
            WITH latest_evals AS (
                SELECT DISTINCT ON (agent_id) *
                FROM ubec_main.holonic_metrics
                ORDER BY agent_id, evaluation_date DESC
            )
            SELECT 
                AVG(autonomy_integration_score) as autonomy,
                AVG(multi_scale_score) as multi_scale,
                AVG(regenerative_impact_score) as regenerative,
                AVG(network_contribution_score) as network,
                AVG(ubuntu_alignment_score) as ubuntu,
                AVG(composite_score) as composite
            FROM latest_evals
            """
            
            # Use DatabaseManager's execute_query method
            avg_scores = self.db_conn.execute_query(query, fetch_one=True)
            
            # Handle the case where no scores are available
            if not avg_scores:
                avg_scores = {
                    'autonomy': 0, 
                    'multi_scale': 0, 
                    'regenerative': 0,
                    'network': 0, 
                    'ubuntu': 0, 
                    'composite': 0
                }
            
            # Build report data structure
            self.report_data = {
                "status": "success",
                "evaluated_count": len(results),
                "evaluation_date": datetime.now().isoformat(),
                "category_distribution": category_distribution,
                "average_scores": avg_scores,
                "results": results
            }
            
            logging.info(f"Loaded evaluation data for {len(results)} agents from database")
            return self.report_data
            
        except Exception as e:
            logging.error(f"Error loading evaluation data from database: {e}")
            # Create empty report structure on error
            self.report_data = {
                "status": "error",
                "evaluated_count": 0,
                "evaluation_date": datetime.now().isoformat(),
                "category_distribution": {},
                "average_scores": {
                    'autonomy': 0, 
                    'multi_scale': 0, 
                    'regenerative': 0,
                    'network': 0, 
                    'ubuntu': 0, 
                    'composite': 0
                },
                "results": [],
                "error": str(e)
            }
            return self.report_data
    
    def create_score_distribution_chart(self, output_file=None):
        """
        Create a histogram of composite scores.
        
        Args:
            output_file: Path to save the chart image
            
        Returns:
            Path to the saved chart or base64 encoded image
        """
        if not self.report_data:
            self.load_evaluation_data_from_db()
            
        if not self.report_data or len(self.report_data.get('results', [])) == 0:
            logging.warning("No evaluation data available for score distribution visualization")
            # Create a simple "No Data" chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "No Data Available", horizontalalignment='center', 
                     verticalalignment='center', transform=plt.gca().transAxes, fontsize=20)
            plt.title('Distribution of Holonic Composite Scores')
            plt.xlabel('Composite Score')
            plt.ylabel('Number of Agents')
            plt.grid(True, alpha=0.3)
            
            # Save or return the chart
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                return output_file
            else:
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                return f"data:image/png;base64,{img_str}"
        
        try:
            # Extract scores from results
            scores = [result.get('composite_score', 0) for result in self.report_data['results']]
            
            # Create plot
            plt.figure(figsize=(10, 6))
            
            # Create histogram
            plt.hist(scores, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            
            # Add category thresholds if available
            if 'thresholds' in self.report_data and 'composite' in self.report_data['thresholds']:
                thresholds = self.report_data['thresholds']['composite']
                for category, threshold in thresholds.items():
                    plt.axvline(x=threshold, color='red', linestyle='--', alpha=0.7)
                    plt.text(threshold, plt.ylim()[1]*0.9, category, rotation=90, verticalalignment='top')
            
            plt.title('Distribution of Holonic Composite Scores')
            plt.xlabel('Composite Score')
            plt.ylabel('Number of Agents')
            plt.grid(True, alpha=0.3)
            
            # Save or return the chart
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                return output_file
            else:
                # Return base64 encoded image
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                return f"data:image/png;base64,{img_str}"
                
        except Exception as e:
            logging.error(f"Error creating score distribution chart: {e}")
            return None
    
    def create_radar_chart(self, output_file=None, top_n=5):
        """
        Create a radar chart of the average scores for each holonic dimension.
        
        Args:
            output_file: Path to save the chart image
            top_n: Number of top agents to include
            
        Returns:
            Path to the saved chart or base64 encoded image
        """
        if not self.report_data:
            self.load_evaluation_data_from_db()
            
        if not self.report_data or len(self.report_data.get('results', [])) == 0:
            logging.warning("No evaluation data available for radar chart visualization")
            # Create a simple "No Data" chart
            plt.figure(figsize=(10, 10))
            plt.text(0.5, 0.5, "No Data Available", horizontalalignment='center', 
                     verticalalignment='center', transform=plt.gca().transAxes, fontsize=20)
            plt.title('Holonic Dimensions Radar Chart')
            
            # Save or return the chart
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                return output_file
            else:
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                return f"data:image/png;base64,{img_str}"
        
        try:
            # Get average scores
            avg_scores = self.report_data.get('average_scores', {})
            if not avg_scores:
                avg_scores = {
                    'autonomy': 0, 'multi_scale': 0, 'regenerative': 0,
                    'network': 0, 'ubuntu': 0, 'composite': 0
                }
            
            # Get top N agents by composite score
            top_agents = sorted(
                self.report_data.get('results', []),
                key=lambda x: x.get('composite_score', 0),
                reverse=True
            )[:top_n]
            
            # Labels for the dimensions
            categories = [
                'Autonomy & Integration', 
                'Multi-scale Participation',
                'Regenerative Impact',
                'Network Contribution',
                'Ubuntu Alignment'
            ]
            
            # Number of variables
            N = len(categories)
            
            # What will be the angle of each axis in the plot
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Close the loop
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
            
            # Helper function to plot one agent
            def add_agent(scores, label, color, alpha=1.0, linewidth=2, linestyle='-'):
                values = [
                    scores.get('autonomy_score', 0),
                    scores.get('multi_scale_score', 0),
                    scores.get('regenerative_score', 0),
                    scores.get('network_score', 0),
                    scores.get('ubuntu_score', 0)
                ]
                values += values[:1]  # Close the loop
                
                ax.plot(angles, values, color=color, linewidth=linewidth, label=label, alpha=alpha, linestyle=linestyle)
                ax.fill(angles, values, color=color, alpha=0.1)
            
            # Plot average scores
            avg_values = [
                avg_scores.get('autonomy', 0),
                avg_scores.get('multi_scale', 0),
                avg_scores.get('regenerative', 0),
                avg_scores.get('network', 0),
                avg_scores.get('ubuntu', 0)
            ]
            avg_values += avg_values[:1]  # Close the loop
            ax.plot(angles, avg_values, color='blue', linewidth=2, label='Community Average', linestyle='-.')
            ax.fill(angles, avg_values, color='blue', alpha=0.1)
            
            # Plot top agents
            colors = cm.rainbow(np.linspace(0, 1, max(1, len(top_agents))))
            for i, agent in enumerate(top_agents):
                agent_scores = {
                    'autonomy_score': agent.get('autonomy_integration_score', 0),
                    'multi_scale_score': agent.get('multi_scale_score', 0),
                    'regenerative_score': agent.get('regenerative_impact_score', 0),
                    'network_score': agent.get('network_contribution_score', 0),
                    'ubuntu_score': agent.get('ubuntu_alignment_score', 0)
                }
                
                # Use account_id or public_key for label
                label = f"{agent.get('account_id', 'Agent')} ({agent.get('holonic_category', 'Unknown')})"
                add_agent(agent_scores, label, colors[i])
            
            # Set chart properties
            ax.set_theta_offset(np.pi / 2)  # Start at top
            ax.set_theta_direction(-1)  # Go clockwise
            
            # Set labels
            plt.xticks(angles[:-1], categories)
            
            # Set y-axis limits
            ax.set_ylim(0, 1)
            
            # Add legend
            plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
            
            plt.title('Holonic Dimensions Radar Chart', size=15, color='black', y=1.1)
            
            # Save or return the chart
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                return output_file
            else:
                # Return base64 encoded image
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                return f"data:image/png;base64,{img_str}"
                
        except Exception as e:
            logging.error(f"Error creating radar chart: {e}")
            return None
    
    def create_category_distribution_chart(self, output_file=None):
        """
        Create a pie chart of holonic category distribution.
        
        Args:
            output_file: Path to save the chart image
            
        Returns:
            Path to the saved chart or base64 encoded image
        """
        if not self.report_data:
            self.load_evaluation_data_from_db()
            
        if not self.report_data or not self.report_data.get('category_distribution'):
            logging.warning("No category distribution data available for visualization")
            # Create a simple "No Data" chart
            plt.figure(figsize=(10, 8))
            plt.text(0.5, 0.5, "No Category Data Available", horizontalalignment='center', 
                     verticalalignment='center', transform=plt.gca().transAxes, fontsize=20)
            plt.title('Distribution of Holonic Categories')
            
            # Save or return the chart
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                return output_file
            else:
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                return f"data:image/png;base64,{img_str}"
        
        try:
            # Get category distribution
            category_dist = self.report_data.get('category_distribution', {})
            
            # If no categories, create a "No Data" chart
            if not category_dist:
                plt.figure(figsize=(10, 8))
                plt.text(0.5, 0.5, "No Category Data Available", horizontalalignment='center', 
                         verticalalignment='center', transform=plt.gca().transAxes, fontsize=20)
                plt.title('Distribution of Holonic Categories')
            
                # Save or return the chart
                if output_file:
                    plt.savefig(output_file, dpi=300, bbox_inches='tight')
                    plt.close()
                    return output_file
                else:
                    buf = BytesIO()
                    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                    plt.close()
                    buf.seek(0)
                    img_str = base64.b64encode(buf.read()).decode('utf-8')
                    return f"data:image/png;base64,{img_str}"
            
            # Define order and colors for categories
            category_order = ['Exemplar', 'Integrator', 'Contributor', 'Participant', 'Observer']
            
            # Filter categories that exist in our data
            labels = []
            sizes = []
            for cat in category_order:
                if cat in category_dist and category_dist[cat] > 0:
                    labels.append(cat)
                    sizes.append(category_dist[cat])
            
            # Define consistent colors for categories
            colors = {
                'Exemplar': '#1f77b4',      # Blue
                'Integrator': '#2ca02c',    # Green
                'Contributor': '#ff7f0e',   # Orange
                'Participant': '#d62728',   # Red
                'Observer': '#9467bd'       # Purple
            }
            
            color_list = [colors.get(cat, '#7f7f7f') for cat in labels]  # Default to gray if category not found
            
            # Create pie chart
            plt.figure(figsize=(10, 8))
            
            # If we have data, create the pie chart
            if sizes:
                # Create pie chart with percentages
                patches, texts, autotexts = plt.pie(
                    sizes, 
                    labels=None,
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=color_list,
                    pctdistance=0.85
                )
                
                # Adjust text properties
                for autotext in autotexts:
                    autotext.set_fontsize(10)
                    autotext.set_fontweight('bold')
                    autotext.set_color('white')
                    
                # Add a circle at the center to create a donut chart
                centre_circle = plt.Circle((0, 0), 0.70, fc='white')
                plt.gca().add_artist(centre_circle)
                
                # Add legend with counts
                legend_labels = [f'{cat} ({sizes[i]})' for i, cat in enumerate(labels)]
                plt.legend(patches, legend_labels, loc='center', bbox_to_anchor=(0.5, 0.5), fontsize=10)
            else:
                plt.text(0.5, 0.5, "No Category Data Available", horizontalalignment='center', 
                         verticalalignment='center', transform=plt.gca().transAxes, fontsize=20)
            
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            plt.title('Distribution of Holonic Categories', size=14)
            
            # Save or return the chart
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                return output_file
            else:
                # Return base64 encoded image
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                return f"data:image/png;base64,{img_str}"
                
        except Exception as e:
            logging.error(f"Error creating category distribution chart: {e}")
            return None
    
    def create_network_visualization(self, output_file=None):
        """
        Create a network visualization of agent transactions.

        Args:
            output_file: Path to save the chart image

        Returns:
            Path to the saved chart or base64 encoded image
        """
        if not self.transaction_network:
            logging.warning("No transaction network available for visualization")
            plt.figure(figsize=(12, 12))
            plt.text(0.5, 0.5, "No Transaction Network Data Available", horizontalalignment='center', 
                     verticalalignment='center', transform=plt.gca().transAxes, fontsize=20)
            plt.title('UBEC Transaction Network')
            plt.axis('off')

            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                return output_file
            else:
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                return f"data:image/png;base64,{img_str}"

        try:
            fig, ax = plt.subplots(figsize=(12, 12))

            scores = nx.get_node_attributes(self.transaction_network, 'reciprocity_score')

            if scores:
                max_score = max(scores.values())
                node_sizes = {node: 100 + (score/max_score)*900 for node, score in scores.items()}
            else:
                node_sizes = {node: 300 for node in self.transaction_network.nodes()}

            weights = nx.get_edge_attributes(self.transaction_network, 'weight')

            if weights:
                max_weight = max(weights.values())
                edge_widths = {edge: 1 + (weight/max_weight)*5 for edge, weight in weights.items()}
            else:
                edge_widths = {edge: 1 for edge in self.transaction_network.edges()}

            layout = nx.spring_layout(self.transaction_network, k=0.15, iterations=50)
            score_values = [scores.get(node, 0) for node in self.transaction_network.nodes()]

            nodes = nx.draw_networkx_nodes(
                self.transaction_network,
                layout,
                ax=ax,
                node_size=[node_sizes.get(node, 300) for node in self.transaction_network.nodes()],
                node_color=score_values,
                cmap=plt.cm.viridis,
                alpha=0.8
            )

            nx.draw_networkx_edges(
                self.transaction_network,
                layout,
                ax=ax,
                width=[edge_widths.get(edge, 1) for edge in self.transaction_network.edges()],
                alpha=0.5,
                edge_color='gray',
                arrowsize=15
            )

            plt.title('UBEC Transaction Network', size=16)
            plt.axis('off')

            if score_values:
                fig.colorbar(nodes, ax=ax, label='Reciprocity Score')

            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                return output_file
            else:
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                return f"data:image/png;base64,{img_str}"

        except Exception as e:
            logging.error(f"Error creating network visualization: {e}")
            plt.figure(figsize=(12, 12))
            plt.text(0.5, 0.5, f"Error creating network visualization: {e}", 
                     horizontalalignment='center', verticalalignment='center', 
                     transform=plt.gca().transAxes, fontsize=14, wrap=True)
            plt.title('UBEC Transaction Network Error', color='red')
            plt.axis('off')

            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                return output_file
            else:
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                return f"data:image/png;base64,{img_str}"


    def generate_html_report(self, output_dir=None):
        """
        Generate a comprehensive HTML report with all visualizations.
        
        Args:
            output_dir: Directory to save the HTML report
            
        Returns:
            Path to the saved HTML report
        """
        if not self.report_data:
            self.load_evaluation_data_from_db()
            
        if not self.report_data:
            logging.error("No evaluation data available for visualization")
            return None
        
        try:
            # Generate visualizations
            score_dist_img = self.create_score_distribution_chart()
            radar_img = self.create_radar_chart()
            category_dist_img = self.create_category_distribution_chart()
            
            network_img = None
            if self.transaction_network:
                network_img = self.create_network_visualization()
            
            # Create directory if it doesn't exist
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            else:
                output_dir = "."
            
            # Define output file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"ubec_holonic_report_{timestamp}.html")
            
            # Ensure required fields exist
            evaluated_count = self.report_data.get('evaluated_count', 0)
            evaluation_date = self.report_data.get('evaluation_date', datetime.now().isoformat())
            avg_scores = self.report_data.get('average_scores', {
                'autonomy': 0, 'multi_scale': 0, 'regenerative': 0,
                'network': 0, 'ubuntu': 0, 'composite': 0
            })
            category_dist = self.report_data.get('category_distribution', {})
            
            # Generate HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>UBEC Holonic Evaluation Report</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        color: #333;
                        line-height: 1.6;
                    }}
                    .container {{
                        width: 90%;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    header {{
                        background-color: #2c3e50;
                        color: white;
                        padding: 1rem;
                        text-align: center;
                    }}
                    h1, h2, h3 {{
                        color: #2c3e50;
                    }}
                    .summary {{
                        background-color: #f8f9fa;
                        padding: 20px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }}
                    .visualization {{
                        margin-bottom: 30px;
                    }}
                    .visualization img {{
                        max-width: 100%;
                        height: auto;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f8f9fa;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        font-size: 0.8rem;
                        color: #777;
                    }}
                    .no-data {{
                        text-align: center;
                        padding: 2rem;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        margin: 1rem 0;
                    }}
                </style>
            </head>
            <body>
                <header>
                    <h1>UBEC Holonic Evaluation Report</h1>
                    <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </header>
                
                <div class="container">
            """
            
            # Add summary section
            html_content += f"""
                    <section class="summary">
                        <h2>Summary</h2>
                        <p>This report contains the results of the holonic evaluation for UBEC token holders.</p>
            """
            
            # Check if we have data
            if evaluated_count > 0:
                html_content += f"""
                        <p><strong>Total Accounts Evaluated:</strong> {evaluated_count}</p>
                        <p><strong>Evaluation Date:</strong> {evaluation_date}</p>
                        
                        <h3>Average Scores</h3>
                        <table>
                            <tr>
                                <th>Dimension</th>
                                <th>Average Score</th>
                            </tr>
                            <tr>
                                <td>Autonomy & Integration</td>
                                <td>{avg_scores.get('autonomy', 0):.4f}</td>
                            </tr>
                            <tr>
                                <td>Multi-scale Participation</td>
                                <td>{avg_scores.get('multi_scale', 0):.4f}</td>
                            </tr>
                            <tr>
                                <td>Regenerative Impact</td>
                                <td>{avg_scores.get('regenerative', 0):.4f}</td>
                            </tr>
                            <tr>
                                <td>Network Contribution</td>
                                <td>{avg_scores.get('network', 0):.4f}</td>
                            </tr>
                            <tr>
                                <td>Ubuntu Alignment</td>
                                <td>{avg_scores.get('ubuntu', 0):.4f}</td>
                            </tr>
                            <tr>
                                <td><strong>Composite Score</strong></td>
                                <td><strong>{avg_scores.get('composite', 0):.4f}</strong></td>
                            </tr>
                        </table>
                """
                
                # Add category distribution table if available
                if category_dist:
                    html_content += """
                        <h3>Category Distribution</h3>
                        <table>
                            <tr>
                                <th>Category</th>
                                <th>Count</th>
                                <th>Percentage</th>
                            </tr>
                    """
                    
                    # Add category distribution data
                    total_count = sum(category_dist.values())
                    for category, count in category_dist.items():
                        percentage = (count / total_count) * 100 if total_count > 0 else 0
                        html_content += f"""
                            <tr>
                                <td>{category}</td>
                                <td>{count}</td>
                                <td>{percentage:.1f}%</td>
                            </tr>
                        """
                    
                    html_content += """
                        </table>
                    """
            else:
                html_content += """
                        <div class="no-data">
                            <h3>No Evaluation Data Available</h3>
                            <p>There are currently no accounts with holonic evaluation data in the database.</p>
                            <p>Please check that the database contains data and that the evaluator is properly configured.</p>
                        </div>
                """
            
            html_content += """
                    </section>
                    
                    <section class="visualizations">
                        <h2>Visualizations</h2>
            """
            
            # Add visualizations
            if score_dist_img:
                html_content += f"""
                        <div class="visualization">
                            <h3>Distribution of Composite Scores</h3>
                            <img src="{score_dist_img}" alt="Score Distribution Chart">
                            <p>This histogram shows the distribution of composite scores across all evaluated accounts.</p>
                        </div>
                """
            
            if radar_img:
                html_content += f"""
                        <div class="visualization">
                            <h3>Holonic Dimensions Radar Chart</h3>
                            <img src="{radar_img}" alt="Radar Chart">
                            <p>This radar chart shows the average scores for each holonic dimension, along with scores for top-performing accounts.</p>
                        </div>
                """
            
            if category_dist_img:
                html_content += f"""
                        <div class="visualization">
                            <h3>Category Distribution</h3>
                            <img src="{category_dist_img}" alt="Category Distribution Chart">
                            <p>This pie chart shows the distribution of accounts across holonic categories.</p>
                        </div>
                """
            
            if network_img:
                html_content += f"""
                        <div class="visualization">
                            <h3>Transaction Network</h3>
                            <img src="{network_img}" alt="Network Visualization">
                            <p>This network visualization shows the transaction relationships between accounts. Node size represents reciprocity score, and edge width represents transaction volume.</p>
                        </div>
                """
            
            html_content += """
                    </section>
            """
            
            # Add top accounts table if we have data
            if evaluated_count > 0:
                html_content += """
                    <section class="top-accounts">
                        <h2>Top Accounts by Composite Score</h2>
                        <table>
                            <tr>
                                <th>Account ID</th>
                                <th>Category</th>
                                <th>Composite Score</th>
                                <th>Autonomy</th>
                                <th>Multi-scale</th>
                                <th>Regenerative</th>
                                <th>Network</th>
                                <th>Ubuntu</th>
                            </tr>
                """
                
                # Add top 20 accounts
                top_accounts = sorted(
                    self.report_data.get('results', []),
                    key=lambda x: x.get('composite_score', 0),
                    reverse=True
                )[:20]
                
                for account in top_accounts:
                    html_content += f"""
                            <tr>
                                <td>{account.get('account_id', 'Unknown')}</td>
                                <td>{account.get('holonic_category', 'Unknown')}</td>
                                <td>{account.get('composite_score', 0):.4f}</td>
                                <td>{account.get('autonomy_integration_score', 0):.4f}</td>
                                <td>{account.get('multi_scale_score', 0):.4f}</td>
                                <td>{account.get('regenerative_impact_score', 0):.4f}</td>
                                <td>{account.get('network_contribution_score', 0):.4f}</td>
                                <td>{account.get('ubuntu_alignment_score', 0):.4f}</td>
                            </tr>
                    """
                
                html_content += """
                        </table>
                    </section>
                """
            
            # Finish HTML
            html_content += """
                    <div class="footer">
                        <p>UBEC Holonic Evaluation System &copy; 2025</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Write HTML to file
            with open(output_file, 'w') as f:
                f.write(html_content)
                
            logging.info(f"HTML report saved to {output_file}")
            return output_file
            
        except Exception as e:
            logging.error(f"Error generating HTML report: {e}")
            return None
