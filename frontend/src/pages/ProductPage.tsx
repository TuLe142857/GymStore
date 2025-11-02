import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axiosClient from "@/utils/axiosClient";
import { Button } from "@/components/ui/button";
import { ShoppingCart, Star } from "lucide-react";
import { useCart } from "@/context/cart-context"; 
import { ProductRecommendationList } from "@/components/ProductRecommendationList";
import { SentimentSummary } from "@/components/SentimentSummary";
import { logInteraction } from "@/utils/interactions";
import { FeedbackList } from "@/components/FeedbackList";
import { FeedbackForm } from "@/components/FeedbackForm";
import { useAuth } from "@/context/auth-context";

// Định nghĩa kiểu dữ liệu cho sản phẩm
interface Product {
  id: string;
  name: string;
  price: number;
  image_url: string;
  category: string;
  description: string;
  rating: number;
}

export default function ProductPage() {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAdding, setIsAdding] = useState(false);
  const { addToCart } = useCart();
  const { isAuthenticated } = useAuth();
  const [feedbackKey, setFeedbackKey] = useState(Date.now());

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setLoading(true);
        setError(null);
        // Giả sử API chi tiết sản phẩm là /product/:id
        const res = await axiosClient.get(`/product/${id}`);
        setProduct(res.data);
        if (id) await logInteraction(id, 'view');
        
      } catch (err) {
        console.error(err);
        setError("Failed to load product details.");
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchProduct();
    }
  }, [id]);

  const handleFeedbackSubmitted = () => {
    setFeedbackKey(Date.now());
  };
  
  const handleAddToCart = async () => {
    if (!product) return;
    setIsAdding(true);
    await addToCart(product.id, 1);
    logInteraction(product.id, 'add_to_cart');
    setIsAdding(false);
  };

  if (loading) {
    return (
      <div className="container mx-auto py-12 px-4 text-center">
        Loading product...
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-12 px-4 text-center text-destructive">
        {error}
      </div>
    );
  }

  if (!product) {
    return (
      <div className="container mx-auto py-12 px-4 text-center">
        Product not found.
      </div>
    );
  }



  return (
    <div className="container mx-auto py-12 px-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Product Image */}
        <div className="bg-muted rounded-lg overflow-hidden h-96 w-96 mx-auto">
          <img
            src={product.image_url || "/placeholder.svg"}
            alt={product.name}
            className="w-full h-full object-cover"
          />
        </div>

        {/* Product Details */}
        <div className="flex flex-col justify-center">
          <span className="text-sm text-muted-foreground mb-2">
            {product.category}
          </span>
          <h1 className="text-3xl md:text-4xl font-bold mb-4">
            {product.name}
          </h1>
          <div className="flex items-center gap-2 mb-4">
            <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
            <span className="font-medium">{product.rating.toFixed(1)}</span>
            <span className="text-muted-foreground">({product.feedbacks?.length || 0} reviews)</span>
          </div>  
          <SentimentSummary productId={product.id} />
          <p className="text-lg text-muted-foreground mb-6">
            {product.description || "No description available."}
          </p>
          <div className="flex items-center justify-between">
            <span className="text-4xl font-bold text-primary">
              ${product.price.toFixed(2)}
            </span>
            <Button size="lg" onClick={handleAddToCart} disabled={isAdding}>
              <ShoppingCart className="w-5 h-5 mr-2" />
              {isAdding ? "Adding..." : "Add to Cart"}
            </Button>
          </div>
        </div>
      </div>
      <ProductRecommendationList
      title="Similar Products"
      endpoint={`/recommend/similar-products/${id}`}
      />
      <div className="mt-12 border-t pt-8">
        <h2 className="text-2xl font-bold mb-6">Customer Feedback</h2>

        {/* Danh sách feedback */}
        <FeedbackList key={feedbackKey} productId={id!} />

        {/* Form gửi feedback (chỉ hiển thị khi user đã đăng nhập) */}
        {isAuthenticated && (
          <div className="mt-8">
            <FeedbackForm
              productId={id!}
              onFeedbackSubmit={handleFeedbackSubmitted}
            />
          </div>
        )}

      </div>
    </div>
  );
}