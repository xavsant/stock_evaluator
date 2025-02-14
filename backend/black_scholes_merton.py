# Imports
import numpy as np
from scipy.stats import norm

# Utility
from io import BytesIO
import matplotlib.pyplot as plt

class BlackScholesMertonModel:
    """
    Calculates the greeks values and plots payoffs of a chosen stock option using the Black-Scholes-Merton model.

    Inputs:
        risk_free_interest_rate (float): The theoretical return of an investment with no risk of financial loss. You may refer to yields on government securities.
        spot_price (float): The current price of a chosen stock.
        strike_price (float): The desired price of a chosen stock.
        time (int): Days to expiration.
        sigma (float): The volatility of a chosen stock. You may refer to financial websites to get the annualised volatility.
        premium (float): The actual contract price for the option.
        position (str): Accepts ['buyer', 'long', 'b'] to buy a stock option and ['seller', 'short', 's'] to sell a stock option (case-insensitive).
        option_type (str): Accepts ['call', 'c'] for a call option and ['put', 'p'] for a put option (case-insensitive).
    
    Methods:
        option_price: Calculates the theoretical price of an option, also known as the premium.
        greeks: Returns greeks [option_price, delta, gamma, vega, theta, rho]. Individual greeks can also be called by using their respective method (e.g. BlackScholesMertonModel.delta()).
        plot_payoff: Plots the payoff graph based on the input variables provided.
    """
    def __init__(self, risk_free_interest_rate: float, spot_price: float, strike_price: float, time: int, sigma: float, \
                 premium: float, position: str = "b", option_type: str = "c"):
        
        # Normalise option_type
        if option_type.lower() in ['call', 'c']:
            self.option_type = 'call'
        elif option_type.lower() in ['put', 'p']:
            self.option_type = 'put'
        else:
            raise ValueError("Invalid option type. Use 'call', 'put', 'c', or 'p'.")

        # Normalise position
        if position.lower() in ['buyer', 'long', 'b']:
            self.position = 'buyer'
        elif position.lower() in ['seller', 'short', 's']:
            self.position = 'seller'
        else:
            raise ValueError("Invalid position. Use 'buyer', 'seller', 'long', 'short', 'b' or 's'.")

        self.risk_free_interest_rate = risk_free_interest_rate
        self.spot_price = spot_price
        self.strike_price = strike_price
        self.time = time/365
        self.sigma = sigma # volatility
        self.premium = premium

    def _d1(self) -> float:
        """
        Intermediate variable for the Black-Scholes-Merton model.
        Represents the normalised distance of the current asset price from the strike price, considering both the drift (adjusted for the risk-free rate) and the volatility of the asset.
        """
        return (np.log(self.spot_price / self.strike_price) + (self.risk_free_interest_rate + self.sigma**2 / 2) * self.time) / (self.sigma * np.sqrt(self.time))

    def _d2(self) -> float:
        """
        Intermediate variable for the Black-Scholes-Merton model.
        Represents the adjusted value of d1 after subtracting the effect of volatility over time
        """
        return self._d1() - self.sigma * np.sqrt(self.time)
    
    def option_price(self) -> float:
        """
        Uses the Black-Scholes-Merton formula to calculate the option price (spot + premium). 
        This value is compared against the real option price provided by the user (spot_price + premium when class is initialised).  
        """
        d1 = self._d1()
        d2 = self._d2()
        if self.option_type in ["c", "call"]:
            price = self.spot_price * norm.cdf(d1) - self.strike_price * np.exp(-self.risk_free_interest_rate * self.time) * norm.cdf(d2)
        elif self.option_type in ["p", "put"]:
            price = self.strike_price * np.exp(-self.risk_free_interest_rate * self.time) * norm.cdf(-d2) - self.spot_price * norm.cdf(-d1)
        else:
            raise ValueError("Invalid option type to calculate greek. Choose 'call' or 'put'")
        return round(float(price), 3)

    def delta(self) -> float:
        d1 = self._d1()
        if self.option_type in ["c", "call"]:
            return round(norm.cdf(d1), 3)
        elif self.option_type in ["p", "put"]:
            return round(-norm.cdf(-d1), 3)
        else:
            raise ValueError("Invalid option type to calculate greek. Choose 'call' or 'put'.")

    def gamma(self) -> float:
        d1 = self._d1()
        return round(norm.pdf(d1) / (self.spot_price * self.sigma * np.sqrt(self.time)), 3)

    def vega(self) -> float:
        d1 = self._d1()
        return round(self.spot_price * norm.pdf(d1) * np.sqrt(self.time) * 0.01, 3)

    def theta(self) -> float:
        d1 = self._d1()
        d2 = self._d2()
        if self.option_type in ["c", "call"]:
            return round((-self.spot_price * norm.pdf(d1) * self.sigma / (2 * np.sqrt(self.time)) - 
                          self.risk_free_interest_rate * self.strike_price * np.exp(-self.risk_free_interest_rate * self.time) * norm.cdf(d2)) / 365, 3)
        elif self.option_type in ["p", "put"]:
            return round((-self.spot_price * norm.pdf(d1) * self.sigma / (2 * np.sqrt(self.time)) + 
                          self.risk_free_interest_rate * self.strike_price * np.exp(-self.risk_free_interest_rate * self.time) * norm.cdf(-d2)) / 365, 3)
        else:
            raise ValueError("Invalid option type to calculate greek. Choose 'call' or 'put'.")

    def rho(self) -> float:
        d2 = self._d2()
        if self.option_type in ["c", "call"]:
            return round(self.strike_price * self.time * np.exp(-self.risk_free_interest_rate * self.time) * norm.cdf(d2) * 0.01, 3)
        elif self.option_type in ["p", "put"]:
            return round(-self.strike_price * self.time * np.exp(-self.risk_free_interest_rate * self.time) * norm.cdf(-d2) * 0.01, 3)
        else:
            raise ValueError("Invalid option type to calculate greek. Choose 'call' or 'put'.")
        
    def greeks(self) -> dict:
        return {
            "option_price": self.option_price(),
            "delta": self.delta(),
            "gamma": self.gamma(),
            "vega": self.vega(),
            "theta": self.theta(),
            "rho": self.rho()
        }
    
    def _calculate_payoff(self, stock_prices) -> float:
        if self.option_type in ("c", "call"):
            payoff = np.maximum(stock_prices - self.strike_price, 0) - self.premium
        elif self.option_type in ("p", "put"):
            payoff = np.maximum(stock_prices - self.spot_price, 0) - self.premium

        if self.position in ("s", "seller"):
            payoff = - payoff

        return payoff

    def plot_payoff(self) -> BytesIO:
        # Define stock price range around the spot price for better focus
        stock_prices = np.linspace(self.spot_price * 0.8, self.spot_price * 1.2, 500)
        
        # Calculate payoffs
        try:
            payoffs = self._calculate_payoff(stock_prices)
        except Exception as e:
            raise ValueError(f"Error in calculating payoffs: {e}")

        # Identify gains and losses
        losses = np.minimum(payoffs, 0)
        gains = np.maximum(payoffs, 0)
        
        # Plot setup
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.fill_between(stock_prices, 0, losses, color='red', alpha=0.2, label="Loss Area")
        ax.fill_between(stock_prices, 0, gains, color='green', alpha=0.2, label="Gain Area")
        ax.plot(stock_prices, payoffs, color='blue', linewidth=1.7)
        ax.axhline(0, color='black', linewidth=1, linestyle='--', label="Break-even Line")
        ax.axvline(self.strike_price, color='red', linewidth=1, linestyle='--', label="Strike Price")
        ax.axvline(self.spot_price, color='blue', linewidth=1, linestyle='--', label="Spot Price")

        # Labels and legend
        ax.set_xlabel("Stock Price at Expiry", fontsize=12)
        ax.set_ylabel("Profit / Loss", fontsize=12)
        ax.legend(facecolor="white", edgecolor="grey", labelcolor="black", loc="best")

        # Change the label colors
        ax.xaxis.label.set_color("white")  # Change X-axis label color
        ax.yaxis.label.set_color("white")  # Change Y-axis label color

        # Customize text, ticks, and spines
        ax = plt.gca()
        ax.tick_params(colors="white")  # Tick colors
        for spine in ax.spines.values():  # Axes lines
            spine.set_color("white")
        ax.set_facecolor("white")  # Black background for axes

        # Set transparent figure background
        fig = plt.gcf()
        fig.patch.set_alpha(0)  # Transparent figure background

        # Save the plot to a buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
        plt.close(fig)
        buf.seek(0)
        
        return buf

if __name__ == "__main__":
    from PIL import Image

    bs_model = BlackScholesMertonModel(risk_free_interest_rate=0.02, spot_price=90.83, strike_price=85.0, time=441, sigma=0.2046, \
                                       premium= 12.5, position="b", option_type="c")
    
    greeks = bs_model.greeks()
    print(greeks)

    # Read and display using matplotlib
    options_payoffs_plot = bs_model.plot_payoff()
    options_payoffs_plot_image = Image.open(options_payoffs_plot)
    plt.imshow(options_payoffs_plot_image)
    plt.axis("off")
    plt.show()
