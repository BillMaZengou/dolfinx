from ffc import *

# Reserved variables for forms
(a, L, M) = (None, None, None)

# Reserved variable for element
element = None

# Copyright (C) 2006-2007 Kristiand B. Oelgaard and Anders Logg.
# Licensed under the GNU LGPL Version 2.1.
#
# First added:  2006-12-05
# Last changed: 2007-05-29
#
# The bilinear form a(v, u) and linear form L(v) for
# Poisson's equation in a discontinuous Galerkin (DG)
# formulation.
#
# Compile this form with FFC: ffc -l dolfin Poisson.form

# Elements
element = FiniteElement("Discontinuous Lagrange", "triangle", 1)

# Test and trial functions
v = TestFunction(element)
u = TrialFunction(element)
f = Function(element)

# Normal component, mesh size and right-hand side
n = FacetNormal("triangle")
h = MeshSize("triangle")

# Parameters
alpha = 4.0
gamma = 8.0

# Bilinear form
a = dot(grad(v), grad(u))*dx \
   - dot(avg(grad(v)), jump(u, n))*dS \
   - dot(jump(v, n), avg(grad(u)))*dS \
   + alpha/h('+')*dot(jump(v, n), jump(u, n))*dS \
   - dot(grad(v), jump(u,n))*ds \
   - dot(jump(v,n), grad(u))*ds \
   + gamma/h*v*u*ds

# Linear form
L = v*f*dx


compile([a, L, M, element], "Poisson", "tensor", "dolfin", {'quadrature_points=': False, 'blas': False, 'precision=': '15', 'optimize': False})
