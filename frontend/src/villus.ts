import { createClient } from 'villus';

const client = createClient({
  url: 'http://[::1]:3000',
});

export default client;
