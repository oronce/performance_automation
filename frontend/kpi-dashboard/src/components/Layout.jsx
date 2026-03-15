import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeSection, setActiveSection] = useState(null);
  const location = useLocation();

  const navigationSections = [
    {
      id: '2g',
      title: '2G Network',
      subsections: [
        { id: '2g-overview', title: 'Overview', path: '/2g/overview' },
        { id: '2g-huawei', title: 'Huawei Performance', path: '/2g/huawei' },
        { id: '2g-ericsson', title: 'Ericsson Performance', path: '/2g/ericsson' },
        { id: '2g-combined', title: 'Combined Analysis', path: '/2g/combined' },
      ],
    },
    {
      id: '3g',
      title: '3G Network',
      subsections: [
        { id: '3g-overview', title: 'Overview', path: '/3g/overview' },
        { id: '3g-simple', title: 'Simple', path: '/3g/simple' },
        { id: '3g-huawei', title: 'Huawei Performance', path: '/3g/huawei' },
      ],
    },
    {
      id: '4g',
      title: '4G Network',
      subsections: [
        { id: '4g-overview', title: 'Overview', path: '/4g/overview' },
        { id: '4g-huawei', title: 'Huawei Performance', path: '/4g/huawei' },
      ],
    },
    {
      id: 'traffic',
      title: 'Traffic Analysis',
      subsections: [
        { id: 'traffic-overview', title: 'Overview', path: '/traffic/overview' },
        { id: 'traffic-data', title: 'Data Traffic', path: '/traffic/data' },
        { id: 'traffic-voice', title: 'Voice Traffic', path: '/traffic/voice' },
      ],
    },
  ];

  const toggleSection = (sectionId) => {
    setActiveSection(activeSection === sectionId ? null : sectionId);
  };

  return (
    <div className="dashboard-layout">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
          <h1 className="dashboard-title">KPI Dashboard</h1>
        </div>
        <div className="header-right">
          <span className="user-info">Admin</span>
        </div>
      </header>

      <div className="dashboard-body">
        {/* Sidebar */}
        {sidebarOpen && (
          <aside className="dashboard-sidebar">
            <nav className="sidebar-nav">
              {navigationSections.map((section) => (
                <div key={section.id} className="nav-section">
                  <button
                    className={`nav-section-header ${
                      activeSection === section.id ? 'active' : ''
                    }`}
                    onClick={() => toggleSection(section.id)}
                  >
                    <span>{section.title}</span>
                    <span className="toggle-icon">
                      {activeSection === section.id ? '▼' : '▶'}
                    </span>
                  </button>

                  {activeSection === section.id && (
                    <div className="nav-subsections">
                      {section.subsections.map((subsection) => (
                        <Link
                          key={subsection.id}
                          to={subsection.path}
                          className={`nav-subsection-link ${
                            location.pathname === subsection.path ? 'active' : ''
                          }`}
                        >
                          {subsection.title}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </nav>
          </aside>
        )}

        {/* Main Content */}
        <main className={`dashboard-main ${sidebarOpen ? '' : 'full-width'}`}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
