import { PICO } from './constants';

function scaleToPico(num) {
  return (num * PICO).toFixed(3);
}

export default scaleToPico;
