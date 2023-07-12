import { computed } from 'vue';

export default function useAuth() {
  const isLoggedIn = computed(() => {
    return !!localStorage.getItem('token');
  });

  return {
    isLoggedIn,
  };
}
