import React from 'react';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton } from '@mui/material';
import { 
  Home as HomeIcon,
  ShowChart as ChartIcon,
  Notifications as AlertsIcon,
  Settings as SettingsIcon,
  ChevronLeft as ChevronLeftIcon
} from '@mui/icons-material';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: 240,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 240,
          boxSizing: 'border-box',
          top: 64,
          height: 'calc(100% - 64px)'
        },
      }}
    >
      <List>
        <ListItem>
          <ListItemIcon>
            <IconButton onClick={onClose}>
              <ChevronLeftIcon />
            </IconButton>
          </ListItemIcon>
        </ListItem>
        <ListItem button>
          <ListItemIcon>
            <HomeIcon />
          </ListItemIcon>
          <ListItemText primary="Dashboard" />
        </ListItem>
        <ListItem button>
          <ListItemIcon>
            <ChartIcon />
          </ListItemIcon>
          <ListItemText primary="Trading" />
        </ListItem>
        <ListItem button>
          <ListItemIcon>
            <AlertsIcon />
          </ListItemIcon>
          <ListItemText primary="Alerts" />
        </ListItem>
        <ListItem button>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItem>
      </List>
    </Drawer>
  );
};

export default Sidebar; 
