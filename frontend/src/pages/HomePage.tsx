import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ProductCard } from "@/components/Product-Card";
import axios from "axios";
import axiosClient from "@/utils/axiosClient";

interface Product {
  id: string;
  name: string;
  price: number;
  image: string;
  category: string;
  rating: number;
}

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // 🔹 Gọi API top-products từ backend
  useEffect(() => {
    const fetchFeaturedProducts = async () => {
      try {
        setLoading(true);
        const res = await axiosClient.get("/recommend/top-products");
        setFeaturedProducts(res.data);
      } catch (err) {
        console.error(err);
        setError("Failed to load products");
      } finally {
        setLoading(false);
      }
    };

    fetchFeaturedProducts();
  }, []);

  // 🔍 Xử lý tìm kiếm
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex-1">
        {/* Hero Section */}
        <section className="bg-gradient-to-r from-primary to-accent py-16 md:py-24">
          <div className="container mx-auto px-4">
            <div className="max-w-2xl">
              <h1 className="text-4xl md:text-5xl font-bold text-primary-foreground mb-4">
                Premium Fitness Supplements
              </h1>
              <p className="text-lg text-primary-foreground/90 mb-8">
                Fuel your fitness journey with high-quality supplements trusted by athletes worldwide.
              </p>
              <Link to="/products">
                <Button size="lg" variant="secondary">
                  Shop Now
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Search Section */}
        <section className="py-8 border-b border-border">
          <div className="container mx-auto px-4">
            <form onSubmit={handleSearch} className="max-w-md">
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    placeholder="Search products..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Button type="submit">Search</Button>
              </div>
            </form>
          </div>
        </section>

        {/* Featured Products */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold mb-2">Featured Products</h2>
            <p className="text-muted-foreground mb-8">
              Discover our best-selling supplements
            </p>

            {loading ? (
              <p className="text-center text-muted-foreground">Loading...</p>
            ) : error ? (
              <p className="text-center text-destructive">{error}</p>
            ) : featuredProducts.length === 0 ? (
              <p className="text-center text-muted-foreground">No products found.</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {featuredProducts.map((product) => (
                  <ProductCard key={product.id} {...product} />
                ))}
              </div>
            )}
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-muted py-12">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-2xl font-bold mb-4">
              Ready to Transform Your Fitness?
            </h2>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Join thousands of athletes who trust GymStore for their supplement needs.
            </p>
            <Link to="/products">
              <Button size="lg">View All Products</Button>
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
