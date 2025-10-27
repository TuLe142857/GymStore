
import { useEffect, useState } from "react";
import axiosClient from "@/utils/axiosClient";
import type { Product } from "@/types";
import { ProductCard } from "@/components/Product-Card";

interface Props {
  title: string;
  endpoint: string;
}

export function ProductRecommendationList({ title, endpoint }: Props) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const fetchRecommendations = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axiosClient.get<Product[]>(endpoint);
        if (mounted) setProducts(res.data);
      } catch (err) {
        console.error(`Failed to fetch ${title}:`, err);
        if (mounted) setError(`Could not load ${title}.`);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    fetchRecommendations();
    return () => {
      mounted = false;
    };
  }, [endpoint, title]);

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <h2 className="text-2xl font-bold mb-4">{title}</h2>
        <p>Loading recommendations...</p>
      </div>
    );
  }

  // Ẩn block nếu lỗi hoặc rỗng
  if (error || products.length === 0) return null;

  return (
    <div className="container mx-auto py-8">
      <h2 className="text-2xl font-bold mb-4">{title}</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {products.map((product) => (
          <ProductCard
            key={product.id}
            id={String(product.id)}
            name={product.name}
            price={product.price}
            image={product.image}
            category={product.category}
            rating={product.rating}
          />
        ))}
      </div>
    </div>
  );
}
