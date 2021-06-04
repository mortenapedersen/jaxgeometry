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

def initialize(M):
    """ Brownian motion in coordinates """

    def sde_Brownian_coords(c,y):
        t,x,chart = c
        dW = y

        gsharpx = M.gsharp((x,chart))
        X = jnp.linalg.cholesky(gsharpx)
        det = -.5*jnp.tensordot(gsharpx,M.Gamma_g((x,chart)),((0,1),(0,1)))
        sto = jnp.tensordot(X,dW,(1,0))
        return (det,sto,X)
    
    def chart_update_Brownian_coords(x,chart,y):
        if M.do_chart_update is None:
            return (x,chart)

        update = M.do_chart_update(x)
        new_chart = M.centered_chart(M.F((x,chart)))
        new_x = M.update_coords((x,chart),new_chart)[0]

        return (jnp.where(update,
                                new_x,
                                x),
                jnp.where(update,
                                new_chart,
                                chart))
    
    M.sde_Brownian_coords = sde_Brownian_coords
    M.chart_update_Brownian_coords = chart_update_Brownian_coords
    M.Brownian_coords = jit(lambda x,dWt: integrate_sde(sde_Brownian_coords,integrator_ito,chart_update_Brownian_coords,x[0],x[1],dWt))