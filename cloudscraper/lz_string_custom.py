import struct

class CustomLZString:
    @staticmethod
    def compress_to_encoded_uri_component(uncompressed, key):
        if uncompressed is None:
            return ""
        # The key acts as the map for the 6-bit values. 
        # key is a string argument, acting as the alphabet.
        return CustomLZString._compress(uncompressed, 6, lambda i: key[i])

    @staticmethod
    def _compress(uncompressed, bits_per_char, get_char_from_int):
        if uncompressed is None:
            return ""

        # Convert input string to a list of UTF-16 code units (integers)
        # to ensure compatibility with JS-based LZString implementations.
        b = uncompressed.encode('utf-16-le')
        # Format '<' is little-endian, 'H' is unsigned short (2 bytes)
        uncompressed_units = struct.unpack(f'<{len(b)//2}H', b)

        i = 0
        context_dictionary = {}
        context_dictionary_to_create = {}
        context_c = ""
        context_wc = ""
        context_w = ""
        context_enlarge_in = 2  # Compensate for the first slot check
        context_dict_size = 3
        context_num_bits = 2
        
        # Checks if key exists in dictionary. 
        # Using string keys for dictionary to match standard LZString logic logic (chars or char sequences)
        # But here our "chars" are integers (utf16 units).
        # We will use string representation of the tuple/list for dict keys or just tuples.
        
        context_data = []
        context_data_val = 0
        context_data_position = 0

        # Helper to append bits to output
        def write_bit(val):
            nonlocal context_data_val, context_data_position
            context_data_val = (context_data_val << 1) | val
            if context_data_position == bits_per_char - 1:
                context_data_position = 0
                context_data.append(get_char_from_int(context_data_val))
                context_data_val = 0
            else:
                context_data_position += 1

        def write_bits(num_bits, val):
             for _ in range(num_bits):
                write_bit(val & 1)
                val = val >> 1

        for ii in range(len(uncompressed_units)):
            context_c = uncompressed_units[ii]
            # We use tuples as dictionary keys for sequences of chars
            # Single char is tuple (c,)
            context_c_key = (context_c,)
            
            if context_c_key not in context_dictionary:
                context_dictionary[context_c_key] = context_dict_size
                context_dict_size += 1
                context_dictionary_to_create[context_c_key] = True
            
            # content_wc = context_w + context_c
            # context_w is a string in JS, here a tuple of ints
            if context_w == "":
                context_wc_key = (context_c,)
            else:
                context_wc_key = context_w + (context_c,)
            
            if context_wc_key in context_dictionary:
                context_w = context_wc_key
            else:
                if context_w in context_dictionary_to_create:
                    if context_w[0] < 256:
                        write_bits(context_num_bits, 0)
                        write_bits(8, context_w[0])
                    else:
                        write_bits(context_num_bits, 1)
                        write_bits(16, context_w[0])
                    context_enlarge_in -= 1
                    if context_enlarge_in == 0:
                        context_enlarge_in = 2**context_num_bits
                        context_num_bits += 1
                    del context_dictionary_to_create[context_w]
                else:
                    write_bits(context_num_bits, context_dictionary[context_w])
                
                context_enlarge_in -= 1
                if context_enlarge_in == 0:
                    context_enlarge_in = 2**context_num_bits
                    context_num_bits += 1
                
                # Add wc to the dictionary.
                context_dictionary[context_wc_key] = context_dict_size
                context_dict_size += 1
                context_w = (context_c,)

        # Output the code for w
        if context_w != "":
            if context_w in context_dictionary_to_create:
                if context_w[0] < 256:
                    write_bits(context_num_bits, 0)
                    write_bits(8, context_w[0])
                else:
                    write_bits(context_num_bits, 1)
                    write_bits(16, context_w[0])
                context_enlarge_in -= 1
                if context_enlarge_in == 0:
                    context_enlarge_in = 2**context_num_bits
                    context_num_bits += 1
                del context_dictionary_to_create[context_w]
            else:
                write_bits(context_num_bits, context_dictionary[context_w])
            
            context_enlarge_in -= 1
            if context_enlarge_in == 0:
                context_enlarge_in = 2**context_num_bits
                context_num_bits += 1

        # Mark the end of the stream
        write_bits(context_num_bits, 2)

        # Flush the last char
        while True:
            context_data_val = (context_data_val << 1)
            if context_data_position == bits_per_char - 1:
                context_data.append(get_char_from_int(context_data_val))
                break
            context_data_position += 1

        return "".join(context_data)
