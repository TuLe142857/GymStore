import React from "react";
import { Link } from "react-router-dom";

const Footer: React.FC = () => {
  return (
    <footer className="bg-muted border-t border-border">
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <Link
              to="/"
              className="flex items-center gap-2 font-bold text-xl text-primary"
            >
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground font-bold">
                GS
              </div>
              <span>GymStore</span>
            </Link>
            <p className="text-muted-foreground text-sm mt-2">
              Premium Fitness Supplements.
            </p>
          </div>
          <nav className="flex gap-4">
            <Link
              to="/products"
              className="text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              Products
            </Link>
            <Link
              to="/about"
              className="text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              About
            </Link>
            <Link
              to="/contact"
              className="text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              Contact
            </Link>
          </nav>
        </div>
        <div className="mt-8 border-t border-border/50 pt-4 text-center">
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} GymStore. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;