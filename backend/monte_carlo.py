# Imports
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.colors
import plotly.graph_objects as go

# Utility
from io import BytesIO

# Fetch Stock Data (for demo purposes + type hinting)
from backend.utils.data_fetching import StockData

class MonteCarloSimulation:
    def __init__(self, stock_data: StockData, num_simulations=100, timeframe=100, initial_portfolio=10000):
        if not isinstance(stock_data, StockData):
            raise TypeError("Expected an instance of the StockData class.")
        self.stock_data = stock_data
        self.stock_num = self.stock_data.stock_num
        self.num_sim = num_simulations
        self.time = timeframe
        self.init_port = initial_portfolio
        self.sims_matrix = self._create_simulation_matrix()
        self.final_values = self.sims_matrix[-1]

    def _create_simulation_matrix(self):
        mean_matrix = np.full(shape=(self.time, self.stock_num), fill_value=self.stock_data.mean_returns).T
        sims_matrix = np.zeros((self.time, self.num_sim))

        for m in range(self.num_sim):
            Z = np.random.normal(size=(self.time, self.stock_data.stock_num))
            L = np.linalg.cholesky(self.stock_data.cov_matrix)
            daily_returns = mean_matrix + np.inner(L, Z)
            sims_matrix[:, m] = np.cumprod(np.inner(self.stock_data.weights, daily_returns.T) + 1) * self.init_port
        return sims_matrix

    def plot_simulation_lines(self, return_as_json: bool = True):
        """Generates interactive simulation lines using Plotly."""
        days = list(range(self.sims_matrix.shape[0]))
        fig = go.Figure()

        color_scale = plotly.colors.sample_colorscale("Spectral", np.linspace(0, 1, self.sims_matrix.shape[1]))
        for i in range(self.sims_matrix.shape[1]):
            fig.add_trace(go.Scatter(
                x=days,
                y=self.sims_matrix[:, i],
                mode='lines',
                line=dict(color=color_scale[i], width=1.5),
                showlegend=False,
            ))

        fig.update_layout(
            title="Monte Carlo Simulations",
            xaxis_title="Days",
            yaxis_title="Portfolio Value (USD)",
            yaxis=dict(range=[self.sims_matrix.min() - 100, self.sims_matrix.max() + 100]),
            template="plotly_white"
        )

        formatted_fig = self._return_format(fig, return_as_json = return_as_json)
        return formatted_fig

    def plot_simulation_avg(self, return_as_json: bool = True):
        """Generates interactive average simulation plot using Plotly."""
        average_values = np.mean(self.sims_matrix, axis=1)
        days = list(range(len(average_values)))
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=days,
            y=average_values,
            mode='lines+markers',
            name='Average Portfolio Value',
            line=dict(color='blue'),
        ))
        fig.add_annotation(
            x=days[-1],
            y=average_values[-1],
            text=f"End Value: ${average_values[-1]:.2f}",
            showarrow=True,
            arrowhead=2,
            ax=-50, ay=-40
        )
        fig.update_layout(
            title="Average Simulated Portfolio Value",
            xaxis_title="Days",
            yaxis_title="Portfolio Value (USD)",
            template="plotly_white"
        )

        formatted_fig = self._return_format(fig, return_as_json = return_as_json)
        return formatted_fig

    def plot_histogram_with_risk_metrics(self, return_as_json: bool = True):
        """Generates histogram with VaR and CVaR using Plotly."""
        VaR_5 = np.percentile(self.final_values, 5)
        CVaR_5 = self.final_values[self.final_values <= VaR_5].mean()
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=self.final_values,
            nbinsx=30,
            marker=dict(color="skyblue", line=dict(color="black", width=1)),
        ))
        fig.add_vline(x=VaR_5, line=dict(color="red", dash="dash"))
        fig.add_vline(x=CVaR_5, line=dict(color="orange", dash="dash"))
        fig.update_layout(
            title="Histogram of Final Portfolio Values with VaR and CVaR",
            xaxis_title="Final Portfolio Value",
            yaxis_title="Frequency",
            template="plotly_white"
        )

        formatted_fig = self._return_format(fig, return_as_json = return_as_json)
        return formatted_fig
    
    def corr_heatmap(self):
        """Generates a static correlation heatmap as an image buffer."""
        plt.figure(figsize=(8, 8))
        sns.heatmap(
            self.stock_data.corr_matrix,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            square=True,
            xticklabels=self.stock_data.stocks,
            yticklabels=self.stock_data.stocks,
            vmin=-1,
            vmax=1,
            cbar_kws={'label': 'Correlation Coefficient'}
        )
        plt.title("Stock Correlation Matrix")
        
        # Save to a buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
        plt.close()
        buf.seek(0)
        return buf
    
    def display_risk_metrics_table_with_insights(self):
        # Calculate risk metrics
        std_dev = np.std(self.final_values)
        mean_return = np.mean(self.final_values)
        sharpe_ratio = (mean_return - self.init_port) / std_dev

        # Generate insights
        insights = []
        if std_dev < 1000:
            insights.append("Low portfolio volatility indicates stable performance.")
        elif std_dev < 2000:
            insights.append("Moderate portfolio volatility; keep an eye on market conditions.")
        else:
            insights.append("High portfolio volatility; diversification might reduce risk.")

        if sharpe_ratio > 1:
            insights.append("Excellent risk-adjusted returns; the portfolio is performing well.")
        elif sharpe_ratio > 0.5:
            insights.append("Decent risk-adjusted returns; consider small optimizations.")
        else:
            insights.append("Low risk-adjusted returns; revisit strategy or rebalance.")

        # Create the table for metrics
        fig, ax = plt.subplots()
        ax.axis('tight')
        ax.axis('off')
        table_data = [
            ["Metric", "Value"],
            ["Standard Deviation", f"${std_dev:.2f}"],
            ["Mean Final Value", f"${mean_return:.2f}"],
            ["Sharpe Ratio", f"{sharpe_ratio:.2f}"]
        ]
        table = ax.table(cellText=table_data, colLabels=None, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.5, 1.5)
        plt.title("Risk Metrics Summary with Insights")
        
        # Add insights as annotations
        for i, insight in enumerate(insights, start=1):
            plt.figtext(0.5, 0.1 - (i * 0.05), f"{i}. {insight}", wrap=True, horizontalalignment='center', fontsize=10)

        # Save to a buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
        plt.close()
        buf.seek(0)
        return buf
    
    def _return_format(self, fig, return_as_json: bool):
        if return_as_json:
            return fig.to_json()  # Return as JSON string for API use
        else:
            return fig


if __name__ == "__main__":
    # This demo mimics the backend to frontend process
    from datetime import datetime, timedelta
    import plotly.io as pio
    from PIL import Image

    # Initialize the StockData class
    stock_symbols = ['AAPL', 'MSFT', 'GOOG']  # Replace with any valid stock symbols
    start_date = datetime.now() - timedelta(days=365)  # Data from the last year
    stock_data = StockData(stock_list=stock_symbols, start_date=start_date)

    # Print the data to verify it works
    print("Mean Returns:", stock_data.mean_returns)
    print("Covariance Matrix:", stock_data.cov_matrix)
    print("Correlation Matrix:", stock_data.corr_matrix)

    # Initialize the MonteCarlo class
    monte_carlo = MonteCarloSimulation(stock_data=stock_data, num_simulations=100, timeframe=365)

    # INTERACTIVE PLOTS
    # Generate interactive plots
    plot_simulation_lines = monte_carlo.plot_simulation_lines(return_as_json = False)
    plot_simulation_avg = monte_carlo.plot_simulation_avg(return_as_json = False)
    plot_histogram_with_risk_metrics = monte_carlo.plot_histogram_with_risk_metrics(return_as_json = False)

    # Save the generated JSON files locally for testing
    pio.write_json(plot_simulation_lines, "notebooks/monte_carlo/simulation_lines.json")
    pio.write_json(plot_simulation_avg, "notebooks/monte_carlo/simulation_avg.json")
    pio.write_json(plot_histogram_with_risk_metrics, "notebooks/monte_carlo/histogram_with_risk_metrics.json")

    print("JSON files have been saved for frontend testing!")
    print("Loading plots...")

    # Load the JSON files
    plot_simulation_lines_json = pio.read_json("notebooks/monte_carlo/simulation_lines.json")
    plot_simulation_avg_json = pio.read_json("notebooks/monte_carlo/simulation_avg.json")
    plot_histogram_with_risk_metrics_json = pio.read_json("notebooks/monte_carlo/histogram_with_risk_metrics.json")
    
    # Run the JSON files
    plot_simulation_lines_json.show()
    plot_simulation_avg_json.show()
    plot_histogram_with_risk_metrics_json.show()

    # STILL PLOTS
    # Generate still plots
    correlation_matrix = monte_carlo.corr_heatmap()
    risk_metrics_tables = monte_carlo.display_risk_metrics_table_with_insights()

    # Read and display using matplotlib
    correlation_matrix_image = Image.open(correlation_matrix)
    plt.imshow(correlation_matrix_image)
    plt.axis("off")
    plt.show()

    risk_metrics_tables_image = Image.open(risk_metrics_tables)
    plt.imshow(risk_metrics_tables_image)
    plt.axis("off")
    plt.show()

    print("Plots displayed!")