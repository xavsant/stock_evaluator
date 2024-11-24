# Imports
import numpy as np
from scipy.stats import norm
import opstrat as op

# Utility
from io import BytesIO
import matplotlib.pyplot as plt

class BlackScholesMertonModel:
    def __init__(self, r, S, K, T, sigma, type_option="c"):
        self.r = r
        self.S = S
        self.K = K
        self.T = T/365
        self.sigma = sigma
        self.type_option = type_option

    def _d1(self):
        return (np.log(self.S / self.K) + (self.r + self.sigma**2 / 2) * self.T) / (self.sigma * np.sqrt(self.T))

    def _d2(self):
        return self._d1() - self.sigma * np.sqrt(self.T)

    def option_price(self):
        d1 = self._d1()
        d2 = self._d2()
        if self.type_option in ["c", "Call"]:
            price = self.S * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        elif self.type_option in ["p", "Put"]:
            price = self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
        else:
            raise ValueError("Please confirm option type [Call (c) or Put (p)]")
        return round(float(price), 3)

    def delta(self):
        d1 = self._d1()
        if self.type_option in ["c", "Call"]:
            return round(norm.cdf(d1), 3)
        elif self.type_option in ["p", "Put"]:
            return round(-norm.cdf(-d1), 3)
        else:
            raise ValueError("Please confirm option type [Call (c) or Put (p)]")

    def gamma(self):
        d1 = self._d1()
        return round(norm.pdf(d1) / (self.S * self.sigma * np.sqrt(self.T)), 3)

    def vega(self):
        d1 = self._d1()
        return round(self.S * norm.pdf(d1) * np.sqrt(self.T) * 0.01, 3)

    def theta(self):
        d1 = self._d1()
        d2 = self._d2()
        if self.type_option in ["c", "Call"]:
            return round((-self.S * norm.pdf(d1) * self.sigma / (2 * np.sqrt(self.T)) - 
                          self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(d2)) / 365, 3)
        elif self.type_option in ["p", "Put"]:
            return round((-self.S * norm.pdf(d1) * self.sigma / (2 * np.sqrt(self.T)) + 
                          self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-d2)) / 365, 3)
        else:
            raise ValueError("Please confirm option type [Call (c) or Put (p)]")

    def rho(self):
        d2 = self._d2()
        if self.type_option in ["c", "Call"]:
            return round(self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(d2) * 0.01, 3)
        elif self.type_option in ["p", "Put"]:
            return round(-self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-d2) * 0.01, 3)
        else:
            raise ValueError("Please confirm option type [Call (c) or Put (p)]")
        
    def greeks(self):
        return {
            "option_price": self.option_price(),
            "delta": self.delta(),
            "gamma": self.gamma(),
            "vega": self.vega(),
            "theta": self.theta(),
            "rho": self.rho()
        }
        
    def plot_option_price(self, tr_type, op_pr):
        op.single_plotter(spot=self.option_price(), strike=self.K, op_type=self.type_option, 
                          tr_type=tr_type, op_pr=op_pr)
        
        # Save to a buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
        plt.close()
        buf.seek(0)
        return buf
        
    def _evaluate_fraction(self, value):
        if isinstance(value, str): # if '/' included
            try:
                return eval(value)
            except (SyntaxError, NameError):
                raise ValueError(f"Invalid fraction: {value}")
        return value

if __name__ == "__main__":
    bs_model = BlackScholesMertonModel(r=0.02, S=90.83, K=40.0, T=441, sigma=0.2046, type_option="c")
    print("Option Price:", bs_model.option_price())
    print("Delta:", bs_model.delta())
    print("Gamma:", bs_model.gamma())
    print("Vega:", bs_model.vega())
    print("Theta:", bs_model.theta())
    print("Rho:", bs_model.rho())

    bs_model.plot_option_price(tr_type="b", op_pr = 12.5)
