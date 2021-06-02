## This file is part of Jax Geometry
#
# Copyright (C) 2021, Stefan Sommer (sommer@di.ku.dk)
# https://bitbucket.org/stefansommer/jaxgeometry
#
# Jax Geometry is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jax Geometry is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Theano Geometry. If not, see <http://www.gnu.org/licenses/>.
#


from src.setup import *
from src.utils import *
from src.linalg import *

def initialize(M,truncate_high_order_derivatives=False):
    """ add metric related structures to manifold """


    d = M.dim

    if hasattr(M, 'g'):
        if not hasattr(M, 'gsharp'):
            M.gsharp = lambda x: jnp.linalg.inv(M.g(x))
    elif hasattr(M, 'gsharp'):
        if not hasattr(M, 'g'):
            M.g = lambda x: jnp.linalg.inv(M.gsharp(x))
    else:
        raise ValueError('no metric or cometric defined on manifold')

    M.Dg = jacfwdx(M.g) # derivative of metric

    ##### Measure
    M.mu_Q = lambda x: 1./jnp.nlinalg.Det()(M.g(x))

    ### Determinant
    M.determinant = lambda x,A: jnp.nlinalg.Det()(jnp.tensordot(M.g(x),A,(1,0)))
    M.LogAbsDeterminant = lambda x,A: LogAbsDet()(jnp.tensordot(M.g(x),A,(1,0)))

    ##### Sharp and flat map:
    M.flat = lambda x,v: jnp.dot(M.g(x),v)
    M.sharp = lambda x,p: jnp.dot(M.gsharp(x),p)

    ##### Christoffel symbols
    # \Gamma^i_{kl}, indices in that order
    M.Gamma_g = lambda x: 0.5*(jnp.einsum('im,mkl->ikl',M.gsharp(x),M.Dg(x))
                   +jnp.einsum('im,mlk->ikl',M.gsharp(x),M.Dg(x))
                   -jnp.einsum('im,klm->ikl',M.gsharp(x),M.Dg(x)))
    M.DGamma_g = jacfwdx(M.Gamma_g)

    # Inner Product from g
    M.dot = lambda x,v,w: jnp.dot(jnp.dot(M.g(x),w),v)
    M.norm = lambda x,v: jnp.sqrt(M.dot(x,v,v))
    M.dotsharp = lambda x,p,pp: jnp.dot(jnp.dot(M.gsharp(x),pp),p)
    M.conorm = lambda x,p: jnp.sqrt(M.dotsharp(x,p,p))

    ##### Gram-Schmidt and basis
    M.gramSchmidt = lambda x,u: (GramSchmidt_f(M.dotf))(x,u)
    M.orthFrame = lambda x: jnp.slinalg.Cholesky()(M.gsharp(x))

    ##### Hamiltonian
    M.H = lambda q,p: 0.5*jnp.dot(p,jnp.dot(M.gsharp(q),p))

    # gradient, divergence, and Laplace-Beltrami
    M.grad = lambda x,f: M.sharp(x,gradx(f(x)))
    M.div = lambda x,X: jnp.trace(jacfwdx(X(x)))+.5*jnp.dot(X(x),gradx(jnp.linalg.logdet(M.g(x))))
    M.Laplacian = lambda x,f: M.div(x,lambda x: M.grad(x,f))
