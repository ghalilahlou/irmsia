import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../services/api';

const AnalysisContext = createContext();

const initialState = {
  currentAnalysis: null,
  analyses: [],
  loading: false,
  error: null,
  filters: {
    status: 'all',
    dateRange: null,
    patientId: '',
  },
};

const analysisReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_ANALYSES':
      return { ...state, analyses: action.payload };
    case 'ADD_ANALYSIS':
      return { ...state, analyses: [action.payload, ...state.analyses] };
    case 'UPDATE_ANALYSIS':
      return {
        ...state,
        analyses: state.analyses.map(analysis =>
          analysis.id === action.payload.id ? action.payload : analysis
        ),
      };
    case 'SET_CURRENT_ANALYSIS':
      return { ...state, currentAnalysis: action.payload };
    case 'SET_FILTERS':
      return { ...state, filters: { ...state.filters, ...action.payload } };
    case 'CLEAR_FILTERS':
      return { ...state, filters: initialState.filters };
    default:
      return state;
  }
};

export const AnalysisProvider = ({ children }) => {
  const [state, dispatch] = useReducer(analysisReducer, initialState);
  const queryClient = useQueryClient();

  // Fetch analyses
  const { data: analyses = [], isLoading, error } = useQuery(
    ['analyses', state.filters],
    () => api.getAnalyses(state.filters),
    {
      refetchInterval: 5000, // Refetch every 5 seconds
      staleTime: 30000, // Consider data stale after 30 seconds
    }
  );

  // Start analysis mutation
  const startAnalysisMutation = useMutation(
    (data) => api.startAnalysis(data),
    {
      onSuccess: (newAnalysis) => {
        dispatch({ type: 'ADD_ANALYSIS', payload: newAnalysis });
        queryClient.invalidateQueries(['analyses']);
        toast.success('Analyse démarrée avec succès');
      },
      onError: (error) => {
        toast.error('Erreur lors du démarrage de l\'analyse');
        console.error('Start analysis error:', error);
      },
    }
  );

  // Cancel analysis mutation
  const cancelAnalysisMutation = useMutation(
    (analysisId) => api.cancelAnalysis(analysisId),
    {
      onSuccess: (cancelledAnalysis) => {
        dispatch({ type: 'UPDATE_ANALYSIS', payload: cancelledAnalysis });
        queryClient.invalidateQueries(['analyses']);
        toast.success('Analyse annulée');
      },
      onError: (error) => {
        toast.error('Erreur lors de l\'annulation');
        console.error('Cancel analysis error:', error);
      },
    }
  );

  // Get analysis result mutation
  const getAnalysisResultMutation = useMutation(
    (analysisId) => api.getAnalysisResult(analysisId),
    {
      onSuccess: (result) => {
        dispatch({ type: 'UPDATE_ANALYSIS', payload: result });
        queryClient.invalidateQueries(['analyses']);
      },
      onError: (error) => {
        toast.error('Erreur lors de la récupération du résultat');
        console.error('Get analysis result error:', error);
      },
    }
  );

  // Update state when analyses data changes
  useEffect(() => {
    if (analyses) {
      dispatch({ type: 'SET_ANALYSES', payload: analyses });
    }
  }, [analyses]);

  // Update loading state
  useEffect(() => {
    dispatch({ type: 'SET_LOADING', payload: isLoading });
  }, [isLoading]);

  // Update error state
  useEffect(() => {
    dispatch({ type: 'SET_ERROR', payload: error });
  }, [error]);

  const value = {
    ...state,
    startAnalysis: startAnalysisMutation.mutate,
    cancelAnalysis: cancelAnalysisMutation.mutate,
    getAnalysisResult: getAnalysisResultMutation.mutate,
    setCurrentAnalysis: (analysis) => dispatch({ type: 'SET_CURRENT_ANALYSIS', payload: analysis }),
    setFilters: (filters) => dispatch({ type: 'SET_FILTERS', payload: filters }),
    clearFilters: () => dispatch({ type: 'CLEAR_FILTERS' }),
    isLoading: startAnalysisMutation.isLoading || cancelAnalysisMutation.isLoading,
  };

  return (
    <AnalysisContext.Provider value={value}>
      {children}
    </AnalysisContext.Provider>
  );
};

export const useAnalysis = () => {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return context;
}; 