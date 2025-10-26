import { Link } from "react-router-dom";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ShoppingCart } from "lucide-react";
import { useCart } from "@/context/cart-context"; // Import
import React, { useState } from "react"; // Import React và useState

interface ProductCardProps {
  id: string;
  name: string;
  price: number;
  image: string;
  category: string;
  rating: number;
}

export function ProductCard({
  id,
  name,
  price,
  image,
  category,
  rating,
}: ProductCardProps) {
  const { addToCart } = useCart(); // Lấy hàm từ context
  const [isAdding, setIsAdding] = useState(false);

  // Xử lý thêm vào giỏ hàng
  const handleAddToCart = async (e: React.MouseEvent) => {
    e.preventDefault(); // Ngăn thẻ Link bên ngoài kích hoạt
    e.stopPropagation(); // Ngăn sự kiện nổi bọt

    setIsAdding(true);
    try {
      await addToCart(id, 1); // Gọi hàm context
    } catch (error) {
      console.error("Failed to add to cart", error);
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <Link to={`/product/${id}`}>
        <CardContent className="p-0 overflow-hidden bg-muted h-48">
          <img
            src={image || "/placeholder.svg"}
            alt={name}
            className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
          />
        </CardContent>
      </Link>

      <CardFooter className="flex flex-col items-start gap-3 p-4">
        <div className="w-full">
          <p className="text-xs text-muted-foreground mb-1">{category}</p>
          <Link to={`/product/${id}`}>
            <h3 className="font-semibold text-sm hover:text-primary transition-colors line-clamp-2">
              {name}
            </h3>
          </Link>

          <div className="flex items-center gap-1 mt-2">
            <span className="text-xs text-yellow-500">★</span>
            <span className="text-xs text-muted-foreground">
              {rating.toFixed(1)}
            </span>
          </div>
        </div>

        <div className="w-full flex items-center justify-between">
          <span className="font-bold text-lg text-primary">
            ${price.toFixed(2)}
          </span>
          <Button
            size="sm"
            variant="default"
            className="gap-2"
            onClick={handleAddToCart} // Gắn sự kiện click
            disabled={isAdding} // Vô hiệu hóa khi đang thêm
          >
            {isAdding ? (
              "Adding..."
            ) : (
              <>
                <ShoppingCart className="w-4 h-4" />
                Add
              </>
            )}
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}

export default ProductCard;