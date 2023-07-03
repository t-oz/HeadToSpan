# author: tyler osborne, tyler.osborne@stonybrook.edu
# 07/03/2023

import spacy


def get_final_span(syntactic_head_token, fb_head_token):
    # mention subtree vs children distinction in meeting!
    syntactic_head_subtree = list(syntactic_head_token.subtree)

    relevant_tokens = []

    for token in syntactic_head_subtree:
        if token.dep_ in ['cc', 'conj'] and token.i > fb_head_token.i:
            break
        relevant_tokens.append(token)

    left_edge = relevant_tokens[0].idx
    right_edge = relevant_tokens[-1].idx + len(relevant_tokens[-1].text)

    return left_edge, right_edge


def get_head_span(head_token_offset_start, head_token_offset_end, doc):
    fb_head_token = doc.char_span(head_token_offset_start, head_token_offset_end,
                                  alignment_mode='expand')[0]

    # when above target, eliminate CC or CONJ arcs
    # if on non-FB-target verb mid-traversal, DO take CC or CONJ arcs
    # if hit AUX, don't take CC or CONJ - don't worry for now
    if fb_head_token.dep_ == 'ROOT':
        syntactic_head_token = fb_head_token
    else:
        syntactic_head_token = None
        ancestors = list(fb_head_token.ancestors)
        ancestors.insert(0, fb_head_token)

        if len(ancestors) == 1:
            syntactic_head_token = ancestors[0]
        else:
            for token in ancestors:
                if token.pos_ in ['PRON', 'PROPN', 'NOUN']:
                    syntactic_head_token = token
                    break
                elif token.pos_ in ['VERB', 'AUX']:
                    syntactic_head_token = token
                    break

            if syntactic_head_token is None:
                for token in ancestors:
                    if token.pos_ == 'NUM':
                        syntactic_head_token = token
                        break

    # postprocessing for CC and CONJ -- exclude child arcs with CC or CONJ
    span_start, span_end = get_final_span(syntactic_head_token, fb_head_token)

    return span_start, span_end


if __name__ == '__main__':
    # loading model -- use en_core_web_sm for faster performance; the large model is more accurate, however
    nlp = spacy.load("en_core_web_lg")

    # head = "coming", indices 23-30
    text = "John said that Mary is coming to dinner."

    # parsing raw text to Spacy doc object
    doc = nlp(text)

    # getting span indices
    span_start, span_end = get_head_span(23, 30, doc)

    print(f"Raw sentence: {text}")
    print(f"Head word: {text[23:30]}")
    print(f"Predicted span: {text[span_start:span_end]}")

