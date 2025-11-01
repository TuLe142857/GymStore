

import { useState } from "react";
import axiosClient from "@/utils/axiosClient";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea"; // Giả sử bạn có component này
import { Star } from "lucide-react";

interface Props {
  productId: string;
  onFeedbackSubmit: () => void; // Hàm để báo cho component cha tải lại list
}

export function FeedbackForm({ productId, onFeedbackSubmit }: Props) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (rating === 0) {
      setError("Please select a rating.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await axiosClient.post(`/feedback/product/${productId}`, {
        rating,
        comment,
      });
      // Reset form và báo cho cha
      setRating(0);
      setComment("");
      onFeedbackSubmit();
    } catch (err: any) {
      setError(err.response?.data?.error || "Failed to submit review.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h3 className="text-xl font-semibold">Write a Review</h3>
      <div>
        <label className="block mb-2 font-medium">Your Rating</label>
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <Star
              key={star}
              className={`w-6 h-6 cursor-pointer ${
                (hoverRating || rating) >= star
                  ? "text-yellow-500 fill-yellow-500"
                  : "text-gray-300"
              }`}
              onClick={() => setRating(star)}
              onMouseEnter={() => setHoverRating(star)}
              onMouseLeave={() => setHoverRating(0)}
            />
          ))}
        </div>
      </div>
      <div>
        <label htmlFor="comment" className="block mb-2 font-medium">
          Your Review
        </label>
        <Textarea
          id="comment"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="What did you like or dislike?"
          rows={4}
        />
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}
      <Button type="submit" disabled={loading}>
        {loading ? "Submitting..." : "Submit Review"}
      </Button>
    </form>
  );
}