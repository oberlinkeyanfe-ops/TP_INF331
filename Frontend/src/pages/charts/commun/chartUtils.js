import { Chart } from 'chart.js';

// Formatage des dates
export const formatDate = (dateString, format = 'short') => {
  if (!dateString) return '—';
  
  try {
    const date = new Date(dateString);
    
    if (format === 'short') {
      return date.toLocaleDateString('fr-FR', { 
        day: '2-digit', 
        month: '2-digit' 
      });
    }
    
    if (format === 'long') {
      return date.toLocaleDateString('fr-FR', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    }
    
    return date.toISOString().split('T')[0];
    
  } catch (error) {
    console.warn('Erreur formatage date:', error);
    return '—';
  }
};

// Trier les données par date (chronologique)
export const sortByDate = (data, dateField = 'date', ascending = true) => {
  if (!Array.isArray(data)) return [];
  
  return [...data].sort((a, b) => {
    const dateA = a[dateField] ? new Date(a[dateField]).getTime() : 0;
    const dateB = b[dateField] ? new Date(b[dateField]).getTime() : 0;
    
    return ascending ? dateA - dateB : dateB - dateA;
  });
};

// Calculer la moyenne d'un tableau
export const calculateAverage = (array) => {
  if (!Array.isArray(array) || array.length === 0) return 0;
  
  const sum = array.reduce((acc, val) => acc + (parseFloat(val) || 0), 0);
  return sum / array.length;
};

// Couleurs prédéfinies pour les graphiques
export const chartColors = {
  primary: '#2196F3',
  success: '#4CAF50',
  danger: '#F44336',
  warning: '#FF9800',
  info: '#00BCD4',
  secondary: '#9C27B0',
  
  getDatasetColor(index) {
    const colors = [
      this.primary,
      this.success,
      this.danger,
      this.warning,
      this.info,
      this.secondary
    ];
    return colors[index % colors.length];
  },
  
  getBackgroundColor(index, opacity = 0.1) {
    const color = this.getDatasetColor(index);
    return this.hexToRgba(color, opacity);
  },
  
  hexToRgba(hex, opacity = 1) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
  }
};

// Enregistrer les plugins Chart.js communs
export const registerChartPlugins = () => {
  // Vous pouvez ajouter des plugins globaux ici
};