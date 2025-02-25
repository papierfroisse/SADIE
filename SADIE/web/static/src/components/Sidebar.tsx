import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

// Icons
import DashboardIcon from '@mui/icons-material/Dashboard';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import AssessmentIcon from '@mui/icons-material/Assessment';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SettingsIcon from '@mui/icons-material/Settings';

const drawerWidth = 240;

interface SidebarProps {
  mobileOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedPairs] = React.useState(['BTCUSDT', 'ETHUSDT', 'BNBUSDT']);

  return (
    <>
      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onClose}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            backgroundColor: 'background.paper',
          },
        }}
      >
        <SidebarContent navigate={navigate} location={location} selectedPairs={selectedPairs} />
      </Drawer>

      {/* Desktop Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            backgroundColor: 'background.paper',
            borderRight: '1px solid rgba(255, 255, 255, 0.12)',
          },
        }}
      >
        <SidebarContent navigate={navigate} location={location} selectedPairs={selectedPairs} />
      </Drawer>
    </>
  );
};

interface SidebarContentProps {
  navigate: (path: string) => void;
  location: { pathname: string };
  selectedPairs: string[];
}

const SidebarContent: React.FC<SidebarContentProps> = ({ navigate, location, selectedPairs }) => {
  const mainMenuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Trading View', icon: <ShowChartIcon />, path: '/trading/BTCUSDT' },
    { text: 'Analysis', icon: <AssessmentIcon />, path: '/analysis' },
    { text: 'Alerts', icon: <NotificationsActiveIcon />, path: '/alerts' },
  ];

  return (
    <Box sx={{ overflow: 'auto', mt: 8 }}>
      <List>
        {mainMenuItems.map(item => (
          <ListItem
            button
            key={item.text}
            onClick={() => navigate(item.path)}
            selected={location.pathname === item.path}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>

      <Divider />

      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle2" color="text.secondary">
          Trading Pairs
        </Typography>
      </Box>

      <List>
        {selectedPairs.map(pair => (
          <ListItem
            button
            key={pair}
            onClick={() => navigate(`/trading/${pair}`)}
            selected={location.pathname === `/trading/${pair}`}
          >
            <ListItemIcon>
              <TrendingUpIcon />
            </ListItemIcon>
            <ListItemText primary={pair} />
          </ListItem>
        ))}
      </List>

      <Divider />

      <List>
        <ListItem button onClick={() => navigate('/settings')}>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItem>
      </List>
    </Box>
  );
};
