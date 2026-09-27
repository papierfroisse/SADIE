import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
} from '@mui/material';
import { Order } from '../../types';

interface OrderPanelProps {
  symbol: string;
  currentPrice: number;
  onSubmitOrder: (order: Omit<Order, 'id' | 'status' | 'timestamp'>) => Promise<void>;
}

const OrderPanel: React.FC<OrderPanelProps> = ({ symbol, currentPrice, onSubmitOrder }) => {
  const [orderType, setOrderType] = useState<'market' | 'limit'>('market');
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [quantity, setQuantity] = useState<string>('');
  const [price, setPrice] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await onSubmitOrder({
        symbol,
        type: orderType,
        side,
        quantity: Number(quantity),
        price: orderType === 'limit' ? Number(price) : undefined,
      });
      // Reset form
      setQuantity('');
      setPrice('');
    } catch (err) {
      console.error('Failed to submit order:', err);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Place Order
      </Typography>
      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Order Type</InputLabel>
              <Select
                value={orderType}
                label="Order Type"
                onChange={e => setOrderType(e.target.value as 'market' | 'limit')}
              >
                <MenuItem value="market">Market</MenuItem>
                <MenuItem value="limit">Limit</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Side</InputLabel>
              <Select
                value={side}
                label="Side"
                onChange={e => setSide(e.target.value as 'buy' | 'sell')}
              >
                <MenuItem value="buy">Buy</MenuItem>
                <MenuItem value="sell">Sell</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Quantity"
              type="number"
              value={quantity}
              onChange={e => setQuantity(e.target.value)}
              inputProps={{ step: 'any', min: 0 }}
            />
          </Grid>

          {orderType === 'limit' && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Price"
                type="number"
                value={price}
                onChange={e => setPrice(e.target.value)}
                inputProps={{ step: 'any', min: 0 }}
              />
            </Grid>
          )}

          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Current Price: ${currentPrice.toFixed(2)}
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Button
              fullWidth
              variant="contained"
              color={side === 'buy' ? 'success' : 'error'}
              type="submit"
              disabled={!quantity || (orderType === 'limit' && !price)}
            >
              {side === 'buy' ? 'Buy' : 'Sell'} {symbol}
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default OrderPanel;
