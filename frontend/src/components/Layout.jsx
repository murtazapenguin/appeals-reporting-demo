import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  DocumentTextIcon,
  DocumentCheckIcon,
  ChartBarIcon,
  BuildingOffice2Icon,
  PlusCircleIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const Layout = ({ children, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', path: '/dashboard', icon: HomeIcon },
    { name: 'All Denials', path: '/denials', icon: DocumentTextIcon },
    { name: 'Submitted Appeals', path: '/submitted-appeals', icon: DocumentCheckIcon },
    { name: 'Reporting', path: '/reporting', icon: ChartBarIcon },
    { name: 'Practice Reports', path: '/practices', icon: BuildingOffice2Icon },
  ];

  const isActive = (path) => location.pathname === path || (path !== '/' && location.pathname.startsWith(path + '/'));

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-gray-900/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-[#fc459d] to-purple-600 rounded-xl flex items-center justify-center mr-3">
                <img src="/penguin-logo.svg" alt="PenguinAI" className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">PenguinAI</h1>
                <p className="text-xs text-gray-500">Claim Appeals</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-gray-500 hover:text-gray-700"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              return (
                <button
                  key={item.path}
                  onClick={() => {
                    navigate(item.path);
                    setSidebarOpen(false);
                  }}
                  className={`w-full flex items-center px-4 py-3 rounded-xl transition-all duration-200 ${
                    active
                      ? 'bg-gradient-to-r from-[#fc459d] to-purple-600 text-white shadow-lg'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  <span className="font-medium">{item.name}</span>
                </button>
              );
            })}
          </nav>

          {/* User Section */}
          <div className="px-4 py-4 border-t border-gray-200">
            <button
              onClick={onLogout}
              className="w-full flex items-center px-4 py-3 text-red-600 hover:bg-red-50 rounded-xl transition-all duration-200"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5 mr-3" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-64">
        {/* Top Bar (Mobile) */}
        <div className="sticky top-0 z-30 lg:hidden bg-white border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-gray-500 hover:text-gray-700"
            >
              <Bars3Icon className="w-6 h-6" />
            </button>
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-[#fc459d] to-purple-600 rounded-lg flex items-center justify-center mr-2">
                <img src="/penguin-logo.svg" alt="PenguinAI" className="w-5 h-5" />
              </div>
              <span className="font-bold text-gray-900">PenguinAI</span>
            </div>
            <div className="w-6" />
          </div>
        </div>

        {/* Page Content */}
        <main className="min-h-screen">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
