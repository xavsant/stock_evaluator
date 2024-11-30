# Imports
import numpy as np
from scipy.stats import norm

# Utility
from io import BytesIO
import matplotlib.pyplot as plt

class BlackScholesMertonModel:
    def __init__(self, interest_rate: float, spot_price: float, strike_price: float, time: int, sigma: float, \
                 premium: float, position: str = "b", option_type: str = "c"):
        
        # Normalise option_type
        if option_type.lower() in ['c', 'call']:
            self.option_type = 'call'
        elif option_type.lower() in ['p', 'put']:
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

        self.interest_rate = interest_rate # risk-free
        self.spot_price = spot_price
        self.strike_price = strike_price
        self.time = time/365
        self.sigma = sigma # volatility
        self.premium = premium

    def _d1(self):
        return (np.log(self.spot_price / self.strike_price) + (self.interest_rate + self.sigma**2 / 2) * self.time) / (self.sigma * np.sqrt(self.time))

    def _d2(self):
        return self._d1() - self.sigma * np.sqrt(self.time)
    
    def option_price(self):
        """
        Uses the black-scholes-merton formula to calculate the option price (spot + premium). 
        This value is compared against the real option price provided by the user (spot_price + premium when class is initialised).  
        """
        d1 = self._d1()
        d2 = self._d2()
        if self.option_type in ["c", "call"]:
            price = self.spot_price * norm.cdf(d1) - self.strike_price * np.exp(-self.interest_rate * self.time) * norm.cdf(d2)
        elif self.option_type in ["p", "put"]:
            price = self.strike_price * np.exp(-self.interest_rate * self.time) * norm.cdf(-d2) - self.spot_price * norm.cdf(-d1)
        else:
            raise ValueError("Invalid option type to calculate greek. Choose 'call' or 'put'")
        return round(float(price), 3)

    def delta(self):
        d1 = self._d1()
        if self.option_type in ["c", "call"]:
            return round(norm.cdf(d1), 3)
        elif self.option_type in ["p", "put"]:
            return round(-norm.cdf(-d1), 3)
        else:
            raise ValueError("Invalid option type to calculate greek. Choose 'call' or 'put'.")

    def gamma(self):
        d1 = self._d1()
        return round(norm.pdf(d1) / (self.spot_price * self.sigma * np.sqrt(self.time)), 3)

    def vega(self):
        d1 = self._d1()
        return round(self.spot_price * norm.pdf(d1) * np.sqrt(self.time) * 0.01, 3)

    def theta(self):
        d1 = self._d1()
        d2 = self._d2()
        if self.option_type in ["c", "call"]:
            return round((-self.spot_price * norm.pdf(d1) * self.sigma / (2 * np.sqrt(self.time)) - 
                          self.interest_rate * self.strike_price * np.exp(-self.interest_rate * self.time) * norm.cdf(d2)) / 365, 3)
        elif self.option_type in ["p", "put"]:
            return round((-self.spot_price * norm.pdf(d1) * self.sigma / (2 * np.sqrt(self.time)) + 
                          self.interest_rate * self.strike_price * np.exp(-self.interest_rate * self.time) * norm.cdf(-d2)) / 365, 3)
        else:
            raise ValueError("Invalid option type to calculate greek. Choose 'call' or 'put'.")

    def rho(self):
        d2 = self._d2()
        if self.option_type in ["c", "call"]:
            return round(self.strike_price * self.time * np.exp(-self.interest_rate * self.time) * norm.cdf(d2) * 0.01, 3)
        elif self.option_type in ["p", "put"]:
            return round(-self.strike_price * self.time * np.exp(-self.interest_rate * self.time) * norm.cdf(-d2) * 0.01, 3)
        else:
            raise ValueError("Invalid option type to calculate greek. Choose 'call' or 'put'.")
        
    def greeks(self):
        return {
            "option_price": self.option_price(),
            "delta": self.delta(),
            "gamma": self.gamma(),
            "vega": self.vega(),
            "theta": self.theta(),
            "rho": self.rho()
        }
    
    def _calculate_payoff(self, stock_prices):
        if self.option_type in ("c", "call"):
            payoffs = np.maximum(stock_prices - self.strike_price, 0) - self.premium
        elif self.option_type in ("p", "put"):
            payoffs = np.maximum(stock_prices - self.spot_price, 0) - self.premium

        if self.position in ("s", "seller"):
            payoffs = -payoffs

        return payoffs

    def visualize(self):
        stock_prices = np.linspace(0, self.strike_price * 2, 500)
        
        # Calculate payoff
        payoffs = self._calculate_payoff(stock_prices)
        
        # Separate gains and losses for coloring
        losses = np.where(payoffs < 0, payoffs, np.nan)
        gains = np.where(payoffs >= 0, payoffs, np.nan)
        
        # Plot the payoff graph
        plt.figure(figsize=(10, 6))
        plt.plot(stock_prices, losses, label="Losses", color='red', linewidth=2)
        plt.plot(stock_prices, gains, label="Gains", color='green', linewidth=2)
        plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
        plt.axvline(self.strike_price, color='blue', linewidth=0.8, linestyle='--', label="Strike Price")
        plt.title(f"{self.position.capitalize()} Payoff Diagram of a {self.option_type.capitalize()} Option")
        plt.xlabel("Stock Price at Expiry")
        plt.ylabel("Profit / Loss")
        plt.legend()
        plt.grid(visible=False)

        # Save to a buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
        plt.close()
        buf.seek(0)
        return buf
        
    # def plot_option_price(self, tr_type, op_pr):
    #     op.single_plotter(spot=self.option_price(), strike=self.K, op_type=self.type_option, 
    #                       tr_type=tr_type, op_pr=op_pr)
        
    #     # Save to a buffer
    #     buf = BytesIO()
    #     plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    #     plt.close()
    #     buf.seek(0)
    #     return buf
        
    # def _evaluate_fraction(self, value):
    #     if isinstance(value, str): # if '/' included
    #         try:
    #             return eval(value)
    #         except (SyntaxError, NameError):
    #             raise ValueError(f"Invalid fraction: {value}")
    #     return value


if __name__ == "__main__":
    from PIL import Image

    bs_model = BlackScholesMertonModel(interest_rate=0.02, spot_price=90.83, strike_price=40.0, time=441, sigma=0.2046, \
                                       premium= 12.5, position="b", option_type="c")
    
    print("Option Price:", bs_model.option_price()) # theoretical
    print("Delta:", bs_model.delta())
    print("Gamma:", bs_model.gamma())
    print("Vega:", bs_model.vega())
    print("Theta:", bs_model.theta())
    print("Rho:", bs_model.rho())

    # bs_model.plot_option_price(tr_type="b", op_pr = 12.5)

    # Read and display using matplotlib
    options_payoffs_plot = bs_model.visualize()
    options_payoffs_plot_image = Image.open(options_payoffs_plot)
    plt.imshow(options_payoffs_plot_image)
    plt.axis("off")
    plt.show()
