import { useEffect, useState } from "react";
import axiosClient from "@/utils/axiosClient";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [edit, setEdit] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    axiosClient
      .get("/auth/profile")
      .then((res) => {
        setProfile(res.data.data.profile); 
      })
      .catch((err) => {
        console.error("Failed to fetch profile", err);
        // Xử lý lỗi (ví dụ: token hết hạn)
      })
      .finally(() => {
        setIsLoading(false); // Dừng loading dù thành công hay thất bại
      });
  }, []);

  if (isLoading) return <p className="p-6">Loading profile...</p>;

  if (!profile) return <p className="p-6">Could not load profile.</p>;
  return (
    <div className="container mx-auto py-12 px-4 max-w-lg">
      <h1 className="text-3xl font-bold mb-6">My Profile</h1>
      <div className="space-y-4">
        <Input
          value={profile.full_name || ""}
          disabled={!edit}
          onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
        />
        <Input
          value={profile.phone || ""}
          disabled={!edit}
          onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
        />
        <Button onClick={() => (edit ? handleSave() : setEdit(true))}>
          {edit ? "Save" : "Edit"}
        </Button>
      </div>
    </div>
  );
}
