import React from "react";
import { Routes, Route } from "react-router-dom";
import DefaultLayout from "../layouts/DefaultLayout";
import HomePage from "../pages/HomePage";

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Các route bình thường dùng DefaultLayout */}
      <Route element={<DefaultLayout />}>
        <Route path="/" element={<HomePage />} />
      </Route>

    </Routes>
  );
};

export default AppRoutes;

