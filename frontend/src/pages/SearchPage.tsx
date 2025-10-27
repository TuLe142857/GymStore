import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import axiosClient from "@/utils/axiosClient";
import { ProductCard } from "@/components/Product-Card";

export default function SearchPage() {
  const [searchParams] = useSearchParams();
  const q = searchParams.get("q") || "";
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axiosClient
      .get(`/product/?search=${encodeURIComponent(q)}`)
      .then((res) => setProducts(res.data.products))
      .finally(() => setLoading(false));
  }, [q]);

  return (
    <div className="container mx-auto py-12 px-4">
      <h1 className="text-2xl font-bold mb-6">
        Search results for: "{q}"
      </h1>
      {loading ? (
        <p>Loading...</p>
      ) : products.length === 0 ? (
        <p>No products found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((p) => (
            <ProductCard key={p.id} {...p} />
          ))}
        </div>
      )}
    </div>
  );
}
