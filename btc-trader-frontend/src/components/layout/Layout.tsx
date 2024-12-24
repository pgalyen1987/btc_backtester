import React from 'react';
import { Box, AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/strategies', label: 'Strategies' },
    { path: '/settings', label: 'Settings' }
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            BTC Trader
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            {navItems.map(({ path, label }) => (
              <Button
                key={path}
                component={Link}
                to={path}
                color="inherit"
                sx={{
                  textDecoration: 'none',
                  fontWeight: location.pathname === path ? 'bold' : 'normal'
                }}
              >
                {label}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </AppBar>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        {children}
      </Box>
    </Box>
  );
};

export default Layout; 