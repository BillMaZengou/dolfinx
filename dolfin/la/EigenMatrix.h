// Copyright (C) 2015 Chris Richardson and Garth N. Wells
//
// This file is part of DOLFIN.
//
// DOLFIN is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// DOLFIN is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with DOLFIN. If not, see <http://www.gnu.org/licenses/>.

#ifndef __EIGEN_MATRIX_H
#define __EIGEN_MATRIX_H

#include <string>
#include <iomanip>
#include <utility>
#include <vector>
#include <memory>
#include <dolfin/common/MPI.h>
#include <dolfin/common/types.h>
#include <dolfin/common/Timer.h>
#include <dolfin/log/dolfin_log.h>

#include <Eigen/Sparse>

#include "GenericMatrix.h"
#include "GenericVector.h"
#include "EigenVector.h"
#include "SparsityPattern.h"
#include "TensorLayout.h"

namespace dolfin
{

  class EigenMatrix : public GenericMatrix
  {
  public:

    /// Create empty matrix
    EigenMatrix();

    /// Create M x N matrix
    EigenMatrix(std::size_t M, std::size_t N);

    /// Copy constructor
    EigenMatrix(const EigenMatrix& A);

    /// Destructor
    virtual ~EigenMatrix();

    //--- Implementation of the GenericTensor interface ---

    /// Initialize zero tensor using tenor layout
    virtual void init(const TensorLayout& tensor_layout);

    /// Return true if empty
    virtual bool empty() const
    { return size(0) == 0; }

    /// Return size of given dimension
    virtual std::size_t size(std::size_t dim) const;

    /// Return local ownership range
    virtual std::pair<std::size_t, std::size_t>
      local_range(std::size_t dim) const
    { return std::make_pair(0, size(dim)); }

    /// Return number of non-zero entries in matrix
    std::size_t nnz() const;

    /// Set all entries to zero and keep any sparse structure
    virtual void zero();

    /// Finalize assembly of tensor
    virtual void apply(std::string mode);

    /// Return MPI communicator
    virtual MPI_Comm mpi_comm() const
    { return MPI_COMM_SELF; }

    /// Return informal string representation (pretty-print)
    virtual std::string str(bool verbose) const;

    //--- Implementation of the GenericMatrix interface ---

    /// Return copy of matrix
    virtual std::shared_ptr<GenericMatrix> copy() const;

    /// Resize matrix to M x N
    virtual void resize(std::size_t M, std::size_t N);

    /// Initialise vector z to be compatible with the matrix-vector product
    /// y = Ax. In the parallel case, both size and layout are
    /// important.
    ///
    /// *Arguments*
    ///     dim (std::size_t)
    ///         The dimension (axis): dim = 0 --> z = y, dim = 1 --> z = x
    virtual void init_vector(GenericVector& z, std::size_t dim) const;

    /// Get block of values
    virtual void get(double* block, std::size_t m, const dolfin::la_index* rows,
                     std::size_t n, const dolfin::la_index* cols) const;

    /// Set block of values using global indices
    virtual void set(const double* block, std::size_t m,
                     const dolfin::la_index* rows, std::size_t n,
                     const dolfin::la_index* cols);

    /// Set block of values using local indices
    virtual void set_local(const double* block, std::size_t m,
                           const dolfin::la_index* rows, std::size_t n,
                           const dolfin::la_index* cols)
    { set(block, m, rows, n, cols); }

    /// Add block of values using global indices
    virtual void add(const double* block, std::size_t m,
                     const dolfin::la_index* rows, std::size_t n,
                     const dolfin::la_index* cols);

    /// Add block of values using local indices
    virtual void add_local(const double* block, std::size_t m,
                           const dolfin::la_index* rows, std::size_t n,
                           const dolfin::la_index* cols)
    { add(block, m, rows, n, cols); }

    /// Add multiple of given matrix (AXPY operation)
    virtual void axpy(double a, const GenericMatrix& A,
                      bool same_nonzero_pattern);

    /// Return norm of matrix
    virtual double norm(std::string norm_type) const;

    /// Get non-zero values of given row
    virtual void getrow(std::size_t row, std::vector<std::size_t>& columns,
                        std::vector<double>& values) const;

    /// Set values for given row
    virtual void setrow(std::size_t row_idx,
                        const std::vector<std::size_t>& columns,
                        const std::vector<double>& values);

    /// Set given rows (global row indices) to zero
    virtual void zero(std::size_t m, const dolfin::la_index* rows);

    /// Set given rows (local row indices) to zero
    virtual void zero_local(std::size_t m, const dolfin::la_index* rows)
    { zero(m, rows); }

    /// Set given rows to identity matrix
    virtual void ident(std::size_t m, const dolfin::la_index* rows);

    /// Set given rows to identity matrix
    virtual void ident_local(std::size_t m, const dolfin::la_index* rows)
    { ident(m, rows); }

    /// Matrix-vector product, y = Ax
    virtual void mult(const GenericVector& x, GenericVector& y) const;

    /// Matrix-vector product, y = A^T x
    virtual void transpmult(const GenericVector& x, GenericVector& y) const;

    /// Set diagonal of a matrix
    virtual void set_diagonal(const GenericVector& x);

    /// Multiply matrix by given number
    virtual const EigenMatrix& operator*= (double a);

    /// Divide matrix by given number
    virtual const EigenMatrix& operator/= (double a);

    /// Assignment operator
    virtual const GenericMatrix& operator= (const GenericMatrix& A);

    /// Return pointers to underlying compressed storage data
    /// See GenericMatrix for documentation.
    //    virtual boost::tuples::tuple<const std::size_t*, const std::size_t*,
    //                                 const double*, int> data() const;

    //--- Special functions ---

    /// Return linear algebra backend factory
    virtual GenericLinearAlgebraFactory& factory() const;

    //--- Special Eigen functions ---

    /// Return reference to Eigen matrix (const version)
    const Eigen::SparseMatrix<double, Eigen::RowMajor>& mat() const
    { return _matA; }

    /// Return reference to Eigen matrix (non-const version)
    //    Mat& mat()
    //    { return _matA; }

    /// Solve Ax = b out-of-place using Eigen (A is not destroyed)
    //    void solve(EigenVector& x, const EigenVector& b) const;

    /// Solve Ax = b in-place using Eigen(A is destroyed)
    //    void solve_in_place(EigenVector& x, const EigenVector& b);

    /// Compute inverse of matrix
    //    void invert();

    /// Lump matrix into vector m
    //    void lump(EigenVector& m) const;

    /// Compress matrix (eliminate all non-zeros from a sparse matrix)
    //    void compress();

    /// Access value of given entry
    //    double operator() (dolfin::la_index i, dolfin::la_index j) const
    //    { return _matA(i, j); }

    /// Assignment operator
    const EigenMatrix& operator= (const EigenMatrix& A);

  private:

    // Eigen matrix object - row major access
    Eigen::SparseMatrix<double, Eigen::RowMajor> _matA;

  };
  //---------------------------------------------------------------------------
}

#endif
