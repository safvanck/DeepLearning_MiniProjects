import torch
import torch.nn as nn
import torch.optim as optim
from torchtext.datasets import Multi30k
from torchtext.data import Field, BucketIterator
import spacy
import numpy as np
import random
from tqdm import tqdm
import torch.nn.functional as F
from termcolor import colored
from torchtext.data.metrics import bleu_score

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from Neural_Machine_Translation.NMT_RNN_with_Attention_train import EncodeDecoder, Encoder, Decoder, OneStepDecoder, Attention

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def get_test_datasets():
    # Download the language files
    spacy_de = spacy.load('de')
    spacy_en = spacy.load('en')

    # define the tokenizer
    def tokenize_de(text):
        return [token.text for token in spacy_de.tokenizer(text)]

    def tokenize_en(text):
        return [token.text for token in spacy_en.tokenizer(text)]

    # Create the pytext's Field
    source = Field(tokenize=tokenize_de, init_token='<sos>', eos_token='<eos>', lower=True)
    target = Field(tokenize=tokenize_en, init_token='<sos>', eos_token='<eos>', lower=True)

    # Splits the data in Train, Test and Validation data
    _, _, test_data = Multi30k.splits(exts=('.de', '.en'), fields=(source, target))

    return test_data


def create_model_for_inference(source_vocab, target_vocab):
    # Define the required dimensions and hyper parameters
    embedding_dim = 256
    hidden_dim = 1024
    dropout = 0.5

    # Instantiate the models
    attention_model = Attention(hidden_dim, hidden_dim)
    encoder = Encoder(len(source_vocab), embedding_dim, hidden_dim)
    one_step_decoder = OneStepDecoder(len(target_vocab), embedding_dim, hidden_dim, hidden_dim, attention_model)
    decoder = Decoder(one_step_decoder, device)

    model = EncodeDecoder(encoder, decoder)

    model = model.to(device)

    return model


def load_models_and_test_data(file_name):
    test_data = get_test_datasets()
    checkpoint = torch.load(file_name)
    source_vocab = checkpoint['source']
    target_vocab = checkpoint['target']
    model = create_model_for_inference(source_vocab, target_vocab)
    model.load_state_dict(checkpoint['model_state_dict'])

    return model, source_vocab, target_vocab, test_data


def predict(id, model, source_vocab, target_vocab, test_data, display_attn=False, debug=False):
    src = vars(test_data.examples[id])['src']
    trg = vars(test_data.examples[id])['trg']

    # Convert each source token to integer values using the vocabulary
    tokens = ['<sos>'] + [token.lower() for token in src] + ['<eos>']
    src_indexes = [source_vocab.stoi[token] for token in tokens]
    src_tensor = torch.LongTensor(src_indexes).unsqueeze(1).to(device)

    model.eval()

    # Run the forward pass of the encoder
    encoder_outputs, hidden = model.encoder(src_tensor)

    # Take the integer value of <sos> from the target vocabulary.
    trg_index = [target_vocab.stoi['<sos>']]
    next_token = torch.LongTensor(trg_index).to(device)

    attentions = torch.zeros(30, 1, len(src_indexes)).to(device)

    trg_indexes = [trg_index[0]]

    outputs = []
    with torch.no_grad():
        # Use the hidden and cell vector of the Encoder and in loop
        # run the forward pass of the OneStepDecoder until some specified
        # step (say 50) or when <eos> has been generated by the model.
        for i in range(30):
            output, hidden, a = model.decoder.one_step_decoder(next_token, hidden, encoder_outputs)

            attentions[i] = a

            # Take the most probable word
            next_token = output.argmax(1)

            trg_indexes.append(next_token.item())

            predicted = target_vocab.itos[output.argmax(1).item()]
            if predicted == '<eos>':
                break
            else:
                outputs.append(predicted)
    if debug:
        print(colored(f'Ground Truth    = {" ".join(trg)}', 'green'))
        print(colored(f'Predicted Label = {" ".join(outputs)}', 'red'))

    predicted_words = [target_vocab.itos[i] for i in trg_indexes]

    if display_attn:
        display_attention(src, predicted_words[1:-1], attentions[:len(predicted_words) - 1])

    return predicted_words


def display_attention(sentence, translation, attention):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)

    attention = attention.squeeze(1).cpu().detach().numpy()[:-1, 1:-1]

    cax = ax.matshow(attention, cmap='bone')

    ax.tick_params(labelsize=15)
    ax.set_xticklabels([''] + [t.lower() for t in sentence] + [''],
                       rotation=45)
    ax.set_yticklabels([''] + translation + [''])

    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

    plt.show()
    plt.close()


def cal_bleu_score(dataset, model, source_vocab, target_vocab):
    targets = []
    predictions = []

    for i in range(len(dataset)):
        target = vars(test_data.examples[i])['trg']
        predicted_words = predict(i, model, source_vocab, target_vocab, dataset)
        predictions.append(predicted_words[1:-1])
        targets.append([target])

    print(f'BLEU Score: {round(bleu_score(predictions, targets) * 100, 2)}')


if __name__ == '__main__':
    checkpoint_file = 'nmt-model-gru-attention-5.pth'
    model, source_vocab, target_vocab, test_data = load_models_and_test_data(checkpoint_file)
    predict(20, model, source_vocab, target_vocab, test_data, display_attn=True, debug=True)
    predict(14, model, source_vocab, target_vocab, test_data, display_attn=True, debug=True)
    predict(1, model, source_vocab, target_vocab, test_data, display_attn=True, debug=True)

    cal_bleu_score(test_data, model, source_vocab, target_vocab)
