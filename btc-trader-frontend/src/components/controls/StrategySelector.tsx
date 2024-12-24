import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  FormHelperText
} from '@mui/material';

interface StrategySelectorProps {
  value: string;
  onChange: (event: SelectChangeEvent<string>) => void;
  disabled?: boolean;
  error?: string;
}

const StrategySelector: React.FC<StrategySelectorProps> = ({
  value,
  onChange,
  disabled = false,
  error
}) => {
  return (
    <FormControl fullWidth disabled={disabled} error={!!error}>
      <InputLabel>Strategy</InputLabel>
      <Select
        value={value}
        onChange={onChange}
        label="Strategy"
      >
        <MenuItem value="simple_ma">Simple Moving Average</MenuItem>
        <MenuItem value="rsi">RSI Strategy</MenuItem>
        <MenuItem value="combined">Combined Strategy</MenuItem>
      </Select>
      {error && <FormHelperText>{error}</FormHelperText>}
    </FormControl>
  );
};

export default StrategySelector; 