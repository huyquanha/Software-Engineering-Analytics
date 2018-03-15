import numpy

def calc_dist(seqs, maxword):
    Pn = numpy.zeros((maxword,))

    for s in seqs:
        for w in s:
            if w >= maxword: Pn[0] += 1
            else: Pn[w] += 1

    Pn = 1.0 * Pn / sum(Pn) #multiply every element of Pn with 1.0 and divide each of those element with the sum of all of them => get percentage

    return Pn

def generate_noise(n_samples, n_noise, Pn):
    noise = numpy.zeros((n_samples, n_noise), dtype='int64')
    for i in range(n_samples):
        noise[i] = numpy.random.choice(len(Pn), n_noise, p=Pn)

    return noise