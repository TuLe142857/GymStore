
import { useState, useEffect } from "react";
import axiosClient from "@/utils/axiosClient";
import type { Feedback } from "@/types";
import { Star } from "lucide-react";

// Component con để hiển thị sao
const StarRating = ({ rating }: { rating: number }) => (
  <div className="flex items-center gap-0.5">
    {[1, 2, 3, 4, 5].map((star) => (
      <Star
        key={star}
        className={`w-4 h-4 ${
          rating >= star ? "text-yellow-500 fill-yellow-500" : "text-gray-300"
        }`}
      />
    ))}
  </div>
);

interface Props {
  productId: string;
}

export function FeedbackList({ productId }: Props) {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFeedbacks = async () => {
      if (!productId) return;
      setLoading(true);
      try {
        const res = await axiosClient.get(`/feedback/product/${productId}`);
        setFeedbacks(res.data);
      } catch (error) {
        console.error("Failed to fetch feedbacks", error);
      } finally {
        setLoading(false);
      }
    };
    fetchFeedbacks();
  }, [productId]);

  if (loading) return <p>Loading reviews...</p>;
  if (feedbacks.length === 0) return <p>No reviews for this product yet.</p>;

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold">Customer Reviews</h3>
      {feedbacks.map((fb) => (
        <div key={fb.id} className="border-b pb-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-semibold">{fb.user_name}</span>
            <span className="text-xs text-muted-foreground">
              {new Date(fb.created_at).toLocaleDateString()}
            </span>
          </div>
          <StarRating rating={fb.rating} />
          <p className="mt-2 text-sm text-gray-700">{fb.comment}</p>
        </div>
      ))}
    </div>
  );
}