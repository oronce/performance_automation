import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import HuaweiDashboard from './pages/2G/HuaweiDashboard';
import CombinedDashboard from './pages/2G/CombinedDashboard';
import Simple3GDashboard from './pages/3G/Simple3GDashboard';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          {/* Home/Dashboard Route */}
          <Route path="/" element={<Dashboard />} />

          {/* 2G Routes */}
          <Route path="/2g/overview" element={<Dashboard />} />
          <Route path="/2g/huawei" element={<HuaweiDashboard />} />
          <Route path="/2g/ericsson" element={<Dashboard />} />
          <Route path="/2g/combined" element={<CombinedDashboard />} />

          {/* 3G Routes */}
          <Route path="/3g/overview" element={<Dashboard />} />
          <Route path="/3g/simple" element={<Simple3GDashboard />} />
          <Route path="/3g/huawei" element={<Dashboard />} />

          {/* 4G Routes */}
          <Route path="/4g/overview" element={<Dashboard />} />
          <Route path="/4g/huawei" element={<Dashboard />} />

          {/* Traffic Routes */}
          <Route path="/traffic/overview" element={<Dashboard />} />
          <Route path="/traffic/data" element={<Dashboard />} />
          <Route path="/traffic/voice" element={<Dashboard />} />

          {/* 404 Redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
