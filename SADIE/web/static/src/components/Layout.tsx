import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Divider,
  Badge,
  Avatar,
  Tooltip,
  useTheme,
  Chip,
  Menu,
  MenuItem,
  Collapse,
} from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import {
  ShowChart,
  Notifications,
  Settings,
  Menu as MenuIcon,
  AccountCircle,
  Brightness4,
  Brightness7,
  Circle,
  Dashboard as DashboardIcon,
  Speed as MetricsIcon,
  NotificationsActive as AlertsIcon,
  ExpandLess,
  ExpandMore,
  Storage as PrometheusIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useWebSocket } from '../context/WebSocketContext';

const drawerWidth = 240;

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

const Main = styled('main', { shouldForwardProp: prop => prop !== 'open' })<{
  open?: boolean;
}>(({ theme, open }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  marginLeft: `-${drawerWidth}px`,
  width: `calc(100% + ${drawerWidth}px)`,
  ...(open && {
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: 0,
    width: '100%',
  }),
}));

interface LayoutProps {
  children: React.ReactNode;
  onToggleTheme?: () => void;
  isDarkMode?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({ children, onToggleTheme, isDarkMode = false }) => {
  const location = useLocation();
  const [open, setOpen] = React.useState(true);
  const theme = useTheme();
  const { isConnected, lastAlert } = useWebSocket();
  const [notificationCount, setNotificationCount] = React.useState(0);
  const [notificationAnchorEl, setNotificationAnchorEl] = React.useState<null | HTMLElement>(null);
  const [notifications, setNotifications] = React.useState<
    Array<{ id: string; message: string; timestamp: number }>
  >([]);
  const [isNotificationMenuOpen, setIsNotificationMenuOpen] = React.useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  // Limiter le nombre de notifications stockées
  const MAX_NOTIFICATIONS = 10;

  React.useEffect(() => {
    if (lastAlert?.triggered) {
      const newNotification = {
        id: lastAlert.id,
        message: `Alerte ${lastAlert.symbol}: ${lastAlert.condition} ${lastAlert.value}`,
        timestamp: Date.now(),
      };
      setNotifications(prev => [newNotification, ...prev].slice(0, MAX_NOTIFICATIONS));
      setNotificationCount(prev => prev + 1);

      // Notification sonore
      const audio = new Audio('/notification.mp3');
      audio.play().catch(() => {
        // Ignorer l'erreur si l'autoplay est bloqué
      });
    }
  }, [lastAlert]);

  const handleNotificationClick = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationAnchorEl(event.currentTarget);
    setIsNotificationMenuOpen(true);
  };

  const handleNotificationClose = () => {
    setNotificationAnchorEl(null);
    setNotificationCount(0);
    setIsNotificationMenuOpen(false);
  };

  const handleNotificationKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      handleNotificationClick(event as unknown as React.MouseEvent<HTMLElement>);
    }
  };

  const formatNotificationTime = (timestamp: number): string => {
    const now = Date.now();
    const diff = now - timestamp;

    if (diff < 60000) {
      // moins d'une minute
      return "À l'instant";
    } else if (diff < 3600000) {
      // moins d'une heure
      const minutes = Math.floor(diff / 60000);
      return `Il y a ${minutes} minute${minutes > 1 ? 's' : ''}`;
    } else if (diff < 86400000) {
      // moins d'un jour
      const hours = Math.floor(diff / 3600000);
      return `Il y a ${hours} heure${hours > 1 ? 's' : ''}`;
    } else {
      return new Date(timestamp).toLocaleString();
    }
  };

  const handleDrawerToggle = () => {
    setOpen(!open);
  };

  const handleSettingsClick = () => {
    setSettingsOpen(!settingsOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: 'background.default' }}>
      <AppBar
        position="fixed"
        sx={{
          zIndex: theme => theme.zIndex.drawer + 1,
          backgroundColor: theme.palette.background.paper,
          color: theme.palette.text.primary,
          boxShadow: theme.shadows[3],
          width: `calc(100% - ${open ? drawerWidth : 0}px)`,
          ml: open ? `${drawerWidth}px` : 0,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            SADIE - Système d'Analyse de Données et d'Intelligence sur les Exchanges
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Tooltip title={isConnected ? 'WebSocket connecté' : 'WebSocket déconnecté'}>
              <Box sx={{ mr: 2, display: 'flex', alignItems: 'center' }}>
                <Circle sx={{ fontSize: 12, color: isConnected ? 'success.main' : 'error.main', mr: 0.5 }} />
                <Typography variant="caption" color={isConnected ? 'success.main' : 'error.main'}>
                  {isConnected ? 'En ligne' : 'Hors ligne'}
                </Typography>
              </Box>
            </Tooltip>
            <Tooltip title="Notifications">
              <IconButton color="inherit" onClick={handleNotificationClick}>
                <Badge badgeContent={notificationCount} color="error">
                  <Notifications />
                </Badge>
              </IconButton>
            </Tooltip>
            <Tooltip title={isDarkMode ? 'Mode clair' : 'Mode sombre'}>
              <IconButton color="inherit" onClick={onToggleTheme}>
                {isDarkMode ? <Brightness7 /> : <Brightness4 />}
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="persistent"
        anchor="left"
        open={open}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <DrawerHeader>
          <Typography variant="h6" sx={{ flexGrow: 1, ml: 2 }}>
            Menu
          </Typography>
        </DrawerHeader>
        <Divider />
        <List>
          <ListItem button component={Link} to="/" selected={location.pathname === '/'}>
            <ListItemIcon>
              <ShowChart />
            </ListItemIcon>
            <ListItemText primary="Trading Chart" />
          </ListItem>
          
          <ListItem button component={Link} to="/dashboard" selected={location.pathname === '/dashboard'}>
            <ListItemIcon>
              <DashboardIcon />
            </ListItemIcon>
            <ListItemText primary="Tableau de bord" />
          </ListItem>
          
          <ListItem button component={Link} to="/metrics" selected={location.pathname === '/metrics'}>
            <ListItemIcon>
              <MetricsIcon />
            </ListItemIcon>
            <ListItemText primary="Métriques" />
          </ListItem>
          
          <ListItem button component={Link} to="/alerts" selected={location.pathname === '/alerts'}>
            <ListItemIcon>
              <AlertsIcon />
            </ListItemIcon>
            <ListItemText primary="Alertes" />
          </ListItem>
          
          <ListItem button onClick={handleSettingsClick}>
            <ListItemIcon>
              <Settings />
            </ListItemIcon>
            <ListItemText primary="Paramètres" />
            {settingsOpen ? <ExpandLess /> : <ExpandMore />}
          </ListItem>
          
          <Collapse in={settingsOpen} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              <ListItem 
                button 
                component={Link} 
                to="/settings/prometheus" 
                selected={location.pathname === '/settings/prometheus'}
                sx={{ pl: 4 }}
              >
                <ListItemIcon>
                  <PrometheusIcon />
                </ListItemIcon>
                <ListItemText primary="Prometheus" />
              </ListItem>
            </List>
          </Collapse>
        </List>
      </Drawer>
      <Main open={open}>
        <DrawerHeader />
        <Paper
          elevation={0}
          sx={{
            p: 3,
            minHeight: 'calc(100vh - 128px)',
            backgroundColor: 'transparent',
          }}
        >
          {children}
        </Paper>
        <Box
          component="footer"
          sx={{
            py: 2,
            px: 3,
            mt: 'auto',
            backgroundColor: 'background.paper',
            borderTop: `1px solid ${theme.palette.divider}`,
          }}
        >
          <Typography variant="body2" color="text.secondary" align="center">
            © 2024 SADIE Trading. Tous droits réservés.
          </Typography>
        </Box>
      </Main>
    </Box>
  );
};
