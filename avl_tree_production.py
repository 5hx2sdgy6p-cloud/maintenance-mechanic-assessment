"""
AVL Tree - Production-Ready Implementation
==========================================

This module provides a thread-safe, self-balancing binary search tree (AVL tree)
suitable for production environments. It includes comprehensive security measures,
resource limits, and detailed documentation.

Author: Joe (Simply Works AI)
Version: 3.0 (Production)

Security Features:
    - Thread-safe operations using reentrant locks
    - Maximum size limits to prevent memory exhaustion
    - Maximum depth limits to prevent stack overflow
    - Input validation for all public methods
    - Configurable logging to prevent data leakage

Functional Features:
    - O(log n) insert, delete, and search operations
    - Self-balancing using AVL rotations
    - Serialization/deserialization support
    - Iteration protocol support (__iter__, __contains__, __len__)
"""

# =============================================================================
# IMPORTS
# =============================================================================

import threading  # Provides Lock and RLock for thread synchronization.
                  # threading.RLock (reentrant lock) allows the same thread
                  # to acquire the lock multiple times without deadlocking.

import logging    # Python's built-in logging framework for recording events.
                  # We use this instead of print() for production-grade output
                  # that can be configured, filtered, and redirected.

from typing import Optional, Any, List, Iterator, Callable
                  # Type hints for better code documentation and IDE support.
                  # Optional[X] means "X or None"
                  # Any means any type is acceptable
                  # List[X] means a list containing items of type X
                  # Iterator[X] means an iterator that yields items of type X
                  # Callable means a function or method that can be called


# =============================================================================
# MODULE-LEVEL CONFIGURATION
# =============================================================================

# Create a logger specific to this module.
# Using __name__ means the logger is named after the module (e.g., "avl_tree_production")
# This allows fine-grained control over logging for just this module.
logger = logging.getLogger(__name__)


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class AVLTreeError(Exception):
    """
    Base exception class for all AVL tree errors.
    
    By creating a custom exception hierarchy, we allow callers to catch
    AVL-specific errors separately from other exceptions. This is a
    production best practice for library code.
    
    Example:
        try:
            tree.insert(value)
        except AVLTreeError as e:
            # Handle any AVL-specific error
            pass
    """
    pass  # No additional implementation needed; inherits everything from Exception.


class AVLTreeCapacityError(AVLTreeError):
    """
    Raised when the tree has reached its maximum capacity.
    
    This exception is raised when attempting to insert into a tree
    that has reached its max_size limit. This prevents memory exhaustion
    attacks where an attacker floods the tree with insertions.
    """
    pass


class AVLTreeDepthError(AVLTreeError):
    """
    Raised when the tree has reached its maximum depth.
    
    This exception is raised when the tree depth would exceed the safe
    recursion limit. This prevents stack overflow crashes. In a properly
    balanced AVL tree, this should rarely occur unless max_size is set
    very high (depth ≈ 1.44 * log2(n)).
    """
    pass


class AVLTreeKeyError(AVLTreeError):
    """
    Raised when there's an issue with a key (not found, invalid type, etc.).
    
    This provides more context than Python's built-in KeyError and allows
    callers to distinguish between AVL key errors and other KeyErrors.
    """
    pass


# =============================================================================
# AVL NODE CLASS
# =============================================================================

class AVLNode:
    """
    Represents a single node in the AVL tree.
    
    Each node stores:
        - A value (the actual data)
        - References to left and right children
        - The height of the subtree rooted at this node
    
    The height is used to calculate the balance factor, which determines
    when rotations are needed to maintain the AVL property (balance factor
    must be -1, 0, or 1 for every node).
    
    Attributes:
        val: The value stored in this node (must be comparable).
        left: Reference to the left child node (or None).
        right: Reference to the right child node (or None).
        height: The height of the subtree rooted at this node.
    
    Note:
        This class is intentionally simple. All the complex logic lives
        in the AVLTree class. Nodes are just data containers.
    """
    
    # __slots__ is a memory optimization that tells Python exactly which
    # attributes this class will have. This prevents Python from creating
    # a __dict__ for each instance, saving ~100 bytes per node. For a tree
    # with millions of nodes, this adds up significantly.
    __slots__ = ['val', 'left', 'right', 'height']
    
    def __init__(self, key: Any) -> None:
        """
        Initialize a new AVL tree node.
        
        Args:
            key: The value to store in this node. Must be comparable
                 (support < and > operators) with other keys in the tree.
        
        The node starts with:
            - No children (left and right are None)
            - Height of 1 (a single node has height 1)
        
        Note:
            We don't validate the key type here because validation happens
            in the AVLTree class before nodes are created. This keeps the
            Node class simple and fast.
        """
        self.val = key        # Store the value. Named 'val' for brevity in tree operations.
        self.left = None      # Left child starts as None (no left subtree).
        self.right = None     # Right child starts as None (no right subtree).
        self.height = 1       # A single node (leaf) has height 1.
                              # Height is the number of edges on the longest path
                              # from this node to a leaf. A leaf has height 1 in our
                              # implementation (some implementations use 0).

    def __repr__(self) -> str:
        """
        Return a string representation of the node for debugging.
        
        This is called when you print() a node or view it in a debugger.
        
        Returns:
            A string like "AVLNode(42, h=2)" showing the value and height.
        """
        return f"AVLNode({self.val}, h={self.height})"


# =============================================================================
# AVL TREE CLASS
# =============================================================================

class AVLTree:
    """
    A thread-safe, self-balancing binary search tree (AVL tree).
    
    An AVL tree maintains the property that for every node, the heights of
    its left and right subtrees differ by at most 1. This ensures O(log n)
    time complexity for insert, delete, and search operations.
    
    Thread Safety:
        All public methods acquire a reentrant lock (RLock) before modifying
        or reading the tree. This allows safe concurrent access from multiple
        threads. The RLock (vs regular Lock) allows the same thread to call
        multiple methods without deadlocking (e.g., a method that calls
        another public method internally).
    
    Resource Limits:
        - max_size: Maximum number of nodes allowed (prevents memory exhaustion)
        - max_depth: Maximum tree depth allowed (prevents stack overflow)
    
    Attributes:
        root: The root node of the tree (or None if empty).
        size: Current number of nodes in the tree.
        max_size: Maximum allowed nodes (None for unlimited).
        max_depth: Maximum allowed depth (default 1000).
        enable_logging: Whether to log operations (disable in production
                        if keys contain sensitive data).
    
    Example:
        >>> tree = AVLTree(max_size=10000)
        >>> tree.insert(5)
        >>> tree.insert(3)
        >>> tree.insert(7)
        >>> print(tree.search(3))  # Returns the node
        >>> print(len(tree))  # Returns 3
        >>> for value in tree:  # Iterate in sorted order
        ...     print(value)
    """
    
    def __init__(
        self,
        max_size: Optional[int] = None,
        max_depth: int = 1000,
        enable_logging: bool = False
    ) -> None:
        """
        Initialize an empty AVL tree with optional resource limits.
        
        Args:
            max_size: Maximum number of nodes allowed in the tree.
                      If None, no limit is enforced (use with caution).
                      Recommended: Set based on available memory.
                      
            max_depth: Maximum depth the tree can reach. Default is 1000,
                       which is safe for Python's default recursion limit.
                       A balanced AVL tree of depth 1000 can hold ~2^700 nodes,
                       so this is effectively unlimited for practical purposes
                       while still protecting against stack overflow.
                       
            enable_logging: If True, log insert/delete/search operations.
                            Set to False in production if keys may contain
                            sensitive data (PII, tokens, etc.) to prevent
                            data leakage through log files.
        
        Thread Safety:
            The constructor itself is not thread-safe, but this is expected—
            you should create the tree before sharing it between threads.
        """
        # The root node. None means the tree is empty.
        # All tree operations start from the root and traverse down.
        self.root: Optional[AVLNode] = None
        
        # Current size (number of nodes). We track this explicitly rather than
        # computing it each time because counting nodes is O(n) while tracking
        # during insert/delete is O(1).
        self._size: int = 0
        
        # Maximum allowed nodes. Used to prevent memory exhaustion attacks.
        self._max_size: Optional[int] = max_size
        
        # Maximum allowed depth. Used to prevent stack overflow from deep recursion.
        # Python's default recursion limit is ~1000, so we use that as default.
        self._max_depth: int = max_depth
        
        # Controls whether operations are logged. Disabled by default for security.
        self._enable_logging: bool = enable_logging
        
        # Threading lock for synchronization.
        # We use RLock (reentrant lock) instead of Lock because:
        # 1. It allows the same thread to acquire the lock multiple times
        # 2. This is needed when public methods call other public methods
        # 3. It prevents deadlock when code is refactored
        #
        # How RLock works:
        # - First acquire() by a thread: lock is acquired, count = 1
        # - Second acquire() by SAME thread: count = 2 (no blocking)
        # - release(): count decrements, lock released when count = 0
        # - acquire() by DIFFERENT thread: blocks until count = 0
        self._lock: threading.RLock = threading.RLock()
    
    # =========================================================================
    # PYTHON MAGIC METHODS (Dunder Methods)
    # =========================================================================
    # These methods make the AVLTree behave like a built-in Python collection.
    # They enable syntax like: len(tree), for x in tree, if x in tree, etc.
    
    def __len__(self) -> int:
        """
        Return the number of nodes in the tree.
        
        This enables the len() function: len(tree)
        
        Returns:
            The current number of nodes in the tree.
        
        Thread Safety:
            Acquires the lock to ensure we read a consistent value.
            Without the lock, we might read a partially-updated size
            during a concurrent insert or delete.
        
        Time Complexity: O(1)
        """
        with self._lock:  # Acquire lock, automatically released when block exits.
            return self._size
    
    def __contains__(self, key: Any) -> bool:
        """
        Check if a key exists in the tree.
        
        This enables the 'in' operator: if key in tree
        
        Args:
            key: The value to search for.
        
        Returns:
            True if the key exists in the tree, False otherwise.
        
        Thread Safety:
            Uses the search() method which acquires the lock.
        
        Time Complexity: O(log n)
        
        Example:
            >>> tree = AVLTree()
            >>> tree.insert(5)
            >>> print(5 in tree)  # True
            >>> print(10 in tree)  # False
        """
        # We use the internal _search_unlocked method here, but we still
        # need to acquire the lock ourselves.
        with self._lock:
            return self._search_unlocked(self.root, key) is not None
    
    def __iter__(self) -> Iterator[Any]:
        """
        Iterate over all values in the tree in sorted order.
        
        This enables for-loops: for value in tree
        
        Yields:
            Values in ascending sorted order.
        
        Thread Safety:
            Creates a snapshot (list) of values while holding the lock,
            then iterates over the snapshot. This prevents issues with
            concurrent modifications during iteration.
        
        Time Complexity: O(n) to create snapshot, then O(1) per iteration.
        
        Warning:
            The snapshot is created at the start of iteration. If the tree
            is modified during iteration, the iterator will not reflect
            those changes (which is the safe behavior).
        
        Example:
            >>> tree = AVLTree()
            >>> tree.insert(3)
            >>> tree.insert(1)
            >>> tree.insert(2)
            >>> list(tree)  # [1, 2, 3]
        """
        with self._lock:
            # Create a snapshot of all values.
            # We do this inside the lock to get a consistent view.
            snapshot: List[Any] = []
            self._in_order_traversal(self.root, snapshot)
        
        # Iterate over the snapshot OUTSIDE the lock.
        # This allows other threads to modify the tree while we iterate.
        # The caller sees the tree as it was when iteration started.
        for value in snapshot:
            yield value  # yield makes this a generator function.
    
    def __repr__(self) -> str:
        """
        Return a string representation of the tree for debugging.
        
        Returns:
            A string showing the tree size and root value.
        
        Example:
            >>> tree = AVLTree(max_size=100)
            >>> print(tree)  # AVLTree(size=0, root=None, max_size=100)
        """
        with self._lock:
            root_val = self.root.val if self.root else None
            return f"AVLTree(size={self._size}, root={root_val}, max_size={self._max_size})"
    
    # =========================================================================
    # PUBLIC PROPERTIES
    # =========================================================================
    # Properties provide controlled access to internal attributes.
    # They look like attributes but are actually method calls.
    
    @property
    def size(self) -> int:
        """
        Get the current number of nodes in the tree.
        
        This is a read-only property. Use insert() and delete() to modify.
        
        Returns:
            The current number of nodes.
        """
        with self._lock:
            return self._size
    
    @property
    def height(self) -> int:
        """
        Get the current height of the tree.
        
        Returns:
            The height of the tree, or 0 if empty.
        """
        with self._lock:
            return self._get_height(self.root)
    
    @property
    def is_empty(self) -> bool:
        """
        Check if the tree is empty.
        
        Returns:
            True if the tree has no nodes, False otherwise.
        """
        with self._lock:
            return self.root is None
    
    # =========================================================================
    # INPUT VALIDATION
    # =========================================================================
    
    def _validate_key(self, key: Any) -> None:
        """
        Validate that a key can be used in the tree.
        
        A valid key must be comparable (support < and > operators).
        This method raises an exception if the key is invalid.
        
        Args:
            key: The key to validate.
        
        Raises:
            AVLTreeKeyError: If the key is None or not comparable.
        
        Why we validate:
            - None keys would cause confusing errors during comparison
            - Non-comparable keys would raise TypeError deep in the tree
            - Early validation gives clear error messages
        
        Note:
            This method does NOT acquire the lock because it doesn't
            access any tree state. It only examines the key itself.
        """
        # Check for None explicitly.
        # While None is technically comparable in Python 2, it causes
        # issues in Python 3 and is almost never what the caller wants.
        if key is None:
            raise AVLTreeKeyError("Key cannot be None")
        
        # Test that the key is comparable with itself.
        # This catches objects that don't implement __lt__ and __gt__.
        # We do this by actually trying the comparison operations.
        try:
            # These comparisons should both return False for equal values.
            # We don't care about the result; we're just checking if the
            # operations are supported.
            _ = key < key  # Test less-than operator
            _ = key > key  # Test greater-than operator
        except TypeError as e:
            # TypeError is raised when comparison operators aren't defined.
            # We convert this to our custom exception for clarity.
            raise AVLTreeKeyError(
                f"Key must be comparable (support < and > operators): {e}"
            )
    
    # =========================================================================
    # PUBLIC METHODS - INSERT
    # =========================================================================
    
    def insert(self, key: Any) -> bool:
        """
        Insert a key into the AVL tree.
        
        The tree automatically rebalances after insertion to maintain
        the AVL property (balance factor of -1, 0, or 1 for all nodes).
        
        Args:
            key: The value to insert. Must be comparable with existing keys.
        
        Returns:
            True if the key was inserted, False if it was a duplicate.
        
        Raises:
            AVLTreeKeyError: If the key is None or not comparable.
            AVLTreeCapacityError: If the tree has reached max_size.
            AVLTreeDepthError: If insertion would exceed max_depth.
        
        Thread Safety:
            Acquires the lock for the entire operation to ensure atomicity.
        
        Time Complexity: O(log n) average and worst case.
        
        Example:
            >>> tree = AVLTree()
            >>> tree.insert(5)  # True
            >>> tree.insert(5)  # False (duplicate)
        """
        # Validate the key BEFORE acquiring the lock.
        # This is a performance optimization: validation doesn't need
        # exclusive access, so we do it first to minimize lock time.
        self._validate_key(key)
        
        # Acquire the lock for all tree modifications.
        # The 'with' statement ensures the lock is released even if
        # an exception occurs inside the block.
        with self._lock:
            # Check capacity limit.
            # We do this inside the lock to prevent race conditions where
            # two threads both check, both see space, and both insert.
            if self._max_size is not None and self._size >= self._max_size:
                raise AVLTreeCapacityError(
                    f"Tree has reached maximum capacity of {self._max_size} nodes"
                )
            
            # Check depth limit.
            # In a balanced AVL tree, max nodes ≈ 2^depth, so we can
            # calculate if we're approaching the depth limit.
            # A more precise check happens during the actual insertion.
            current_height = self._get_height(self.root)
            if current_height >= self._max_depth:
                raise AVLTreeDepthError(
                    f"Tree has reached maximum depth of {self._max_depth}"
                )
            
            # Track the original size to detect if insertion succeeded.
            original_size = self._size
            
            # Perform the recursive insertion.
            # _insert_recursive returns the new root of the tree (which may
            # change due to rotations) and updates self._size if successful.
            self.root = self._insert_recursive(self.root, key, depth=0)
            
            # Check if the size changed (i.e., insertion was successful).
            inserted = self._size > original_size
            
            # Log the operation if logging is enabled.
            if self._enable_logging:
                if inserted:
                    logger.info(f"Inserted key {key} into AVL tree")
                else:
                    logger.debug(f"Duplicate key {key} not inserted")
            
            return inserted
    
    def _insert_recursive(
        self,
        node: Optional[AVLNode],
        key: Any,
        depth: int
    ) -> AVLNode:
        """
        Recursively insert a key into the subtree rooted at 'node'.
        
        This is the internal recursive implementation of insert. It:
        1. Finds the correct position for the new key
        2. Creates a new node
        3. Updates heights on the way back up
        4. Rebalances if necessary
        
        Args:
            node: The root of the current subtree (may be None).
            key: The key to insert.
            depth: Current depth in the tree (for depth limit checking).
        
        Returns:
            The new root of the subtree after insertion and rebalancing.
            This may be different from 'node' if a rotation occurred.
        
        Raises:
            AVLTreeDepthError: If depth exceeds max_depth.
        
        Note:
            This method assumes the lock is already held by the caller.
            It should only be called from insert().
        
        How recursion works here:
            1. We traverse down the tree, choosing left or right at each node
            2. When we hit None, we create and return the new node
            3. As the recursion unwinds (returns back up), we:
               - Update the height of each node
               - Check and fix balance at each node
            4. The final return gives us the (possibly new) root
        """
        # Check depth limit to prevent stack overflow.
        # Each recursive call increases depth by 1.
        if depth > self._max_depth:
            raise AVLTreeDepthError(
                f"Insertion would exceed maximum depth of {self._max_depth}"
            )
        
        # BASE CASE: We've found the insertion point.
        # When node is None, we've traversed past a leaf.
        # Create and return a new node to be attached by the parent.
        if node is None:
            self._size += 1  # Increment size since we're adding a node.
            return AVLNode(key)  # Return the new node.
        
        # RECURSIVE CASE: Traverse left or right based on comparison.
        if key < node.val:
            # Key is smaller: it belongs in the left subtree.
            # We recursively insert into the left subtree and update
            # node.left with whatever comes back (may be new node or
            # rotated subtree).
            node.left = self._insert_recursive(node.left, key, depth + 1)
        elif key > node.val:
            # Key is larger: it belongs in the right subtree.
            node.right = self._insert_recursive(node.right, key, depth + 1)
        else:
            # Key equals node.val: it's a duplicate.
            # AVL trees typically don't allow duplicates.
            # Return the node unchanged (don't increment size).
            return node
        
        # UPDATE HEIGHT after insertion.
        # The height of a node is 1 plus the maximum height of its children.
        # We must do this BEFORE rebalancing because _rebalance uses heights.
        node.height = 1 + max(
            self._get_height(node.left),
            self._get_height(node.right)
        )
        
        # REBALANCE if necessary.
        # Returns 'node' if balanced, or new subtree root if rotated.
        return self._rebalance(node)
    
    # =========================================================================
    # PUBLIC METHODS - DELETE
    # =========================================================================
    
    def delete(self, key: Any) -> bool:
        """
        Delete a key from the AVL tree.
        
        The tree automatically rebalances after deletion to maintain
        the AVL property.
        
        Args:
            key: The value to delete.
        
        Returns:
            True if the key was found and deleted, False if not found.
        
        Raises:
            AVLTreeKeyError: If the key is None or not comparable.
        
        Thread Safety:
            Acquires the lock for the entire operation.
        
        Time Complexity: O(log n) average and worst case.
        
        Example:
            >>> tree = AVLTree()
            >>> tree.insert(5)
            >>> tree.delete(5)  # True
            >>> tree.delete(5)  # False (not found)
        """
        self._validate_key(key)
        
        with self._lock:
            original_size = self._size
            
            # Perform recursive deletion.
            self.root = self._delete_recursive(self.root, key)
            
            deleted = self._size < original_size
            
            if self._enable_logging:
                if deleted:
                    logger.info(f"Deleted key {key} from AVL tree")
                else:
                    logger.debug(f"Key {key} not found for deletion")
            
            return deleted
    
    def _delete_recursive(
        self,
        node: Optional[AVLNode],
        key: Any
    ) -> Optional[AVLNode]:
        """
        Recursively delete a key from the subtree rooted at 'node'.
        
        Deletion in a BST has three cases:
        1. Node has no children: just remove it
        2. Node has one child: replace node with its child
        3. Node has two children: replace with in-order successor
        
        After deletion, we rebalance on the way back up.
        
        Args:
            node: The root of the current subtree.
            key: The key to delete.
        
        Returns:
            The new root of the subtree after deletion and rebalancing.
            Returns None if the subtree becomes empty.
        
        Note:
            This method assumes the lock is already held.
        """
        # BASE CASE: Key not found.
        # We've traversed past a leaf without finding the key.
        if node is None:
            return None
        
        # SEARCH for the key.
        if key < node.val:
            # Key would be in left subtree.
            node.left = self._delete_recursive(node.left, key)
        elif key > node.val:
            # Key would be in right subtree.
            node.right = self._delete_recursive(node.right, key)
        else:
            # FOUND IT! Now handle the three deletion cases.
            
            # Case 1 & 2: Node has at most one child.
            if node.left is None:
                # No left child: return right child (may be None).
                self._size -= 1
                return node.right
            elif node.right is None:
                # No right child: return left child.
                self._size -= 1
                return node.left
            
            # Case 3: Node has two children.
            # Strategy: Replace this node's value with its in-order successor
            # (smallest value in right subtree), then delete that successor.
            #
            # Why in-order successor? It's the smallest value that's larger
            # than all values in the left subtree, so it maintains BST order.
            
            # Find the in-order successor (minimum in right subtree).
            successor = self._get_min_node(node.right)
            
            # Copy the successor's value to this node.
            # The node isn't actually deleted; its value is replaced.
            node.val = successor.val
            
            # Delete the successor from the right subtree.
            # The successor has at most one child (right), so this is
            # simpler than the general case.
            node.right = self._delete_recursive(node.right, successor.val)
        
        # UPDATE HEIGHT after potential deletion in subtree.
        node.height = 1 + max(
            self._get_height(node.left),
            self._get_height(node.right)
        )
        
        # REBALANCE if necessary.
        return self._rebalance(node)
    
    # =========================================================================
    # PUBLIC METHODS - SEARCH
    # =========================================================================
    
    def search(self, key: Any) -> Optional[AVLNode]:
        """
        Search for a key in the AVL tree.
        
        Args:
            key: The value to search for.
        
        Returns:
            The node containing the key, or None if not found.
        
        Raises:
            AVLTreeKeyError: If the key is None or not comparable.
        
        Thread Safety:
            Acquires the lock during the search.
        
        Time Complexity: O(log n) average and worst case.
        
        Example:
            >>> tree = AVLTree()
            >>> tree.insert(5)
            >>> node = tree.search(5)  # Returns the node
            >>> node = tree.search(10)  # Returns None
        """
        self._validate_key(key)
        
        with self._lock:
            result = self._search_unlocked(self.root, key)
            
            if self._enable_logging:
                if result:
                    logger.debug(f"Key {key} found in AVL tree")
                else:
                    logger.debug(f"Key {key} not found in AVL tree")
            
            return result
    
    def _search_unlocked(
        self,
        node: Optional[AVLNode],
        key: Any
    ) -> Optional[AVLNode]:
        """
        Search for a key without acquiring the lock.
        
        This is an internal method used by search() and __contains__().
        The caller must ensure the lock is held.
        
        Args:
            node: The root of the subtree to search.
            key: The key to search for.
        
        Returns:
            The node containing the key, or None if not found.
        
        Note:
            This is implemented iteratively rather than recursively to
            avoid stack overflow on deep trees and improve performance.
        """
        # Iterative search is used instead of recursive for two reasons:
        # 1. No risk of stack overflow regardless of tree depth
        # 2. Slightly faster (no function call overhead)
        
        current = node  # Start at the given node (usually root).
        
        while current is not None:
            if key == current.val:
                # Found it!
                return current
            elif key < current.val:
                # Key would be in left subtree.
                current = current.left
            else:
                # Key would be in right subtree.
                current = current.right
        
        # Traversed to a None child: key not found.
        return None
    
    # =========================================================================
    # PUBLIC METHODS - TRAVERSAL
    # =========================================================================
    
    def in_order_traversal(self) -> List[Any]:
        """
        Return all values in the tree in sorted (ascending) order.
        
        In-order traversal visits: left subtree, node, right subtree.
        For a BST, this produces sorted output.
        
        Returns:
            A list of all values in ascending order.
        
        Thread Safety:
            Acquires the lock and creates a snapshot.
        
        Time Complexity: O(n) where n is the number of nodes.
        
        Example:
            >>> tree = AVLTree()
            >>> tree.insert(5)
            >>> tree.insert(3)
            >>> tree.insert(7)
            >>> tree.in_order_traversal()  # [3, 5, 7]
        """
        with self._lock:
            result: List[Any] = []
            self._in_order_traversal(self.root, result)
            
            if self._enable_logging:
                logger.debug(f"In-order traversal: {result}")
            
            return result
    
    def _in_order_traversal(
        self,
        node: Optional[AVLNode],
        output: List[Any]
    ) -> None:
        """
        Recursively perform in-order traversal.
        
        Args:
            node: Current node to visit.
            output: List to append values to.
        
        Note:
            Modifies output in place rather than returning a new list.
            This is more memory efficient for large trees.
        """
        if node is not None:
            # Visit left subtree first (smaller values).
            self._in_order_traversal(node.left, output)
            # Visit this node (append its value).
            output.append(node.val)
            # Visit right subtree (larger values).
            self._in_order_traversal(node.right, output)
    
    def pre_order_traversal(self) -> List[Any]:
        """
        Return all values in pre-order (node, left, right).
        
        Pre-order is useful for creating a copy of the tree or
        for serialization that preserves structure.
        
        Returns:
            A list of values in pre-order.
        
        Time Complexity: O(n)
        """
        with self._lock:
            result: List[Any] = []
            self._pre_order_traversal(self.root, result)
            return result
    
    def _pre_order_traversal(
        self,
        node: Optional[AVLNode],
        output: List[Any]
    ) -> None:
        """Recursively perform pre-order traversal."""
        if node is not None:
            output.append(node.val)  # Visit node first.
            self._pre_order_traversal(node.left, output)
            self._pre_order_traversal(node.right, output)
    
    def post_order_traversal(self) -> List[Any]:
        """
        Return all values in post-order (left, right, node).
        
        Post-order is useful for deleting a tree or evaluating
        expression trees.
        
        Returns:
            A list of values in post-order.
        
        Time Complexity: O(n)
        """
        with self._lock:
            result: List[Any] = []
            self._post_order_traversal(self.root, result)
            return result
    
    def _post_order_traversal(
        self,
        node: Optional[AVLNode],
        output: List[Any]
    ) -> None:
        """Recursively perform post-order traversal."""
        if node is not None:
            self._post_order_traversal(node.left, output)
            self._post_order_traversal(node.right, output)
            output.append(node.val)  # Visit node last.
    
    # =========================================================================
    # PRIVATE HELPER METHODS - HEIGHT AND BALANCE
    # =========================================================================
    
    def _get_height(self, node: Optional[AVLNode]) -> int:
        """
        Get the height of a node.
        
        Args:
            node: The node to get height of.
        
        Returns:
            The height of the node, or 0 if node is None.
        
        Note:
            None nodes have height 0. Leaf nodes have height 1.
            This is important for balance factor calculations.
        """
        if node is None:
            return 0
        return node.height
    
    def _get_balance_factor(self, node: Optional[AVLNode]) -> int:
        """
        Calculate the balance factor of a node.
        
        The balance factor is: height(left subtree) - height(right subtree)
        
        In a valid AVL tree, balance factor must be -1, 0, or 1.
        - Positive: left-heavy
        - Negative: right-heavy
        - Zero: perfectly balanced
        
        Args:
            node: The node to calculate balance factor for.
        
        Returns:
            The balance factor, or 0 if node is None.
        """
        if node is None:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)
    
    # =========================================================================
    # PRIVATE HELPER METHODS - ROTATIONS
    # =========================================================================
    #
    # AVL trees maintain balance through four types of rotations:
    #
    # 1. Right Rotation (LL case):
    #    Used when left subtree is too tall and the left child is left-heavy.
    #
    #        z                y
    #       / \              / \
    #      y   T4    =>    x    z
    #     / \             / \  / \
    #    x   T3          T1 T2 T3 T4
    #   / \
    #  T1  T2
    #
    # 2. Left Rotation (RR case):
    #    Mirror image of right rotation.
    #
    # 3. Left-Right Rotation (LR case):
    #    First rotate left on left child, then rotate right on node.
    #
    # 4. Right-Left Rotation (RL case):
    #    First rotate right on right child, then rotate left on node.
    
    def _rotate_right(self, z: AVLNode) -> AVLNode:
        """
        Perform a right rotation around node z.
        
        This is used when the left subtree is too tall (LL or LR case).
        
        Before rotation:
                z
               / \
              y   T4
             / \
            x   T3
        
        After rotation:
                y
               / \
              x   z
                 / \
                T3  T4
        
        Args:
            z: The node to rotate around (the unbalanced node).
        
        Returns:
            y: The new root of this subtree.
        
        Note:
            - y becomes the new root
            - z becomes y's right child
            - y's original right child (T3) becomes z's left child
            - Heights must be updated: z first, then y
        """
        # Store references to the nodes involved.
        y = z.left         # y is z's left child (will become new root).
        T3 = y.right       # T3 is y's right subtree (will move to z's left).
        
        # Perform the rotation.
        y.right = z        # z becomes y's right child.
        z.left = T3        # T3 becomes z's left child.
        
        # Update heights BOTTOM-UP (z first, then y).
        # This is critical: y's height depends on z's new height.
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        
        # Return the new root of this subtree.
        return y
    
    def _rotate_left(self, z: AVLNode) -> AVLNode:
        """
        Perform a left rotation around node z.
        
        This is the mirror image of right rotation.
        Used when the right subtree is too tall (RR or RL case).
        
        Before rotation:
            z
           / \
          T1  y
             / \
            T2  x
        
        After rotation:
              y
             / \
            z   x
           / \
          T1  T2
        
        Args:
            z: The node to rotate around.
        
        Returns:
            y: The new root of this subtree.
        """
        y = z.right        # y is z's right child (will become new root).
        T2 = y.left        # T2 is y's left subtree (will move to z's right).
        
        # Perform the rotation.
        y.left = z         # z becomes y's left child.
        z.right = T2       # T2 becomes z's right child.
        
        # Update heights bottom-up.
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        
        return y
    
    def _rebalance(self, node: AVLNode) -> AVLNode:
        """
        Rebalance the subtree rooted at 'node' if necessary.
        
        This is the core of AVL tree maintenance. After every insert or
        delete, we check if the node violates the AVL property (balance
        factor outside [-1, 1]) and fix it with rotations.
        
        There are four cases:
        
        1. Left-Left (LL): balance > 1 and left child is left-heavy (≥ 0)
           Fix: Single right rotation
        
        2. Left-Right (LR): balance > 1 and left child is right-heavy (< 0)
           Fix: Left rotate left child, then right rotate node
        
        3. Right-Right (RR): balance < -1 and right child is right-heavy (≤ 0)
           Fix: Single left rotation
        
        4. Right-Left (RL): balance < -1 and right child is left-heavy (> 0)
           Fix: Right rotate right child, then left rotate node
        
        Args:
            node: The node to potentially rebalance.
        
        Returns:
            The new root of the subtree (same node if no rotation,
            or the rotated node if rebalancing occurred).
        
        IMPORTANT:
            This implementation uses the balance factor of children to
            determine rotation type, NOT the inserted/deleted key.
            This is the correct approach that works for both insertions
            and deletions.
        """
        # Calculate the balance factor.
        balance = self._get_balance_factor(node)
        
        # Check if rebalancing is needed (|balance| > 1).
        
        # CASE: Left-heavy (balance > 1)
        if balance > 1:
            # Determine if it's LL or LR case by checking left child's balance.
            left_balance = self._get_balance_factor(node.left)
            
            if left_balance >= 0:
                # LL Case: Left child is left-heavy or balanced.
                # Single right rotation fixes this.
                return self._rotate_right(node)
            else:
                # LR Case: Left child is right-heavy.
                # Need double rotation: left-rotate left child, then right-rotate node.
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)
        
        # CASE: Right-heavy (balance < -1)
        if balance < -1:
            # Determine if it's RR or RL case by checking right child's balance.
            right_balance = self._get_balance_factor(node.right)
            
            if right_balance <= 0:
                # RR Case: Right child is right-heavy or balanced.
                # Single left rotation fixes this.
                return self._rotate_left(node)
            else:
                # RL Case: Right child is left-heavy.
                # Need double rotation: right-rotate right child, then left-rotate node.
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)
        
        # No rebalancing needed; return the node unchanged.
        return node
    
    # =========================================================================
    # PRIVATE HELPER METHODS - UTILITIES
    # =========================================================================
    
    def _get_min_node(self, node: AVLNode) -> AVLNode:
        """
        Find the node with the minimum value in the subtree.
        
        In a BST, the minimum is always in the leftmost node.
        
        Args:
            node: The root of the subtree to search.
        
        Returns:
            The node with the smallest value.
        
        Note:
            Assumes node is not None. Caller must check.
        """
        current = node
        # Keep going left until we can't anymore.
        while current.left is not None:
            current = current.left
        return current
    
    def _get_max_node(self, node: AVLNode) -> AVLNode:
        """
        Find the node with the maximum value in the subtree.
        
        In a BST, the maximum is always in the rightmost node.
        
        Args:
            node: The root of the subtree to search.
        
        Returns:
            The node with the largest value.
        """
        current = node
        while current.right is not None:
            current = current.right
        return current
    
    # =========================================================================
    # PUBLIC METHODS - SERIALIZATION
    # =========================================================================
    
    def to_list(self) -> List[Any]:
        """
        Export the tree as a sorted list.
        
        Useful for serialization, debugging, or converting to other formats.
        
        Returns:
            A list of all values in sorted order.
        
        Example:
            >>> tree = AVLTree()
            >>> tree.insert(5)
            >>> tree.insert(3)
            >>> data = tree.to_list()  # [3, 5]
            >>> # Save 'data' to file, send over network, etc.
        """
        return self.in_order_traversal()
    
    def from_list(self, keys: List[Any]) -> None:
        """
        Populate the tree from a list of keys.
        
        This CLEARS the existing tree and inserts all keys from the list.
        
        Args:
            keys: List of values to insert.
        
        Raises:
            AVLTreeKeyError: If any key is invalid.
            AVLTreeCapacityError: If list exceeds max_size.
        
        Example:
            >>> tree = AVLTree()
            >>> tree.from_list([5, 3, 7, 1])
            >>> print(tree.to_list())  # [1, 3, 5, 7]
        """
        with self._lock:
            # Clear the existing tree.
            self.root = None
            self._size = 0
        
        # Insert each key.
        for key in keys:
            self.insert(key)
    
    # =========================================================================
    # PUBLIC METHODS - UTILITY
    # =========================================================================
    
    def clear(self) -> None:
        """
        Remove all nodes from the tree.
        
        After calling this, the tree is empty.
        
        Thread Safety:
            Acquires the lock for the operation.
        """
        with self._lock:
            self.root = None
            self._size = 0
            
            if self._enable_logging:
                logger.info("Cleared AVL tree")
    
    def get_min(self) -> Optional[Any]:
        """
        Get the minimum value in the tree.
        
        Returns:
            The smallest value, or None if tree is empty.
        
        Time Complexity: O(log n)
        """
        with self._lock:
            if self.root is None:
                return None
            return self._get_min_node(self.root).val
    
    def get_max(self) -> Optional[Any]:
        """
        Get the maximum value in the tree.
        
        Returns:
            The largest value, or None if tree is empty.
        
        Time Complexity: O(log n)
        """
        with self._lock:
            if self.root is None:
                return None
            return self._get_max_node(self.root).val
    
    def is_valid_avl(self) -> bool:
        """
        Verify that the tree is a valid AVL tree.
        
        A valid AVL tree must satisfy:
        1. BST property: left < node < right for all nodes
        2. AVL property: |balance factor| <= 1 for all nodes
        3. Height property: heights are correctly calculated
        
        This is useful for testing and debugging.
        
        Returns:
            True if the tree is valid, False otherwise.
        
        Time Complexity: O(n)
        """
        with self._lock:
            return self._validate_avl(self.root, float('-inf'), float('inf'))
    
    def _validate_avl(
        self,
        node: Optional[AVLNode],
        min_val: Any,
        max_val: Any
    ) -> bool:
        """
        Recursively validate AVL properties.
        
        Args:
            node: Current node to validate.
            min_val: Minimum allowed value (exclusive).
            max_val: Maximum allowed value (exclusive).
        
        Returns:
            True if subtree is valid, False otherwise.
        """
        if node is None:
            return True
        
        # Check BST property.
        if node.val <= min_val or node.val >= max_val:
            return False
        
        # Check AVL balance property.
        balance = self._get_balance_factor(node)
        if abs(balance) > 1:
            return False
        
        # Check height is correctly calculated.
        expected_height = 1 + max(
            self._get_height(node.left),
            self._get_height(node.right)
        )
        if node.height != expected_height:
            return False
        
        # Recursively validate children.
        return (
            self._validate_avl(node.left, min_val, node.val) and
            self._validate_avl(node.right, node.val, max_val)
        )
    
    def print_tree(self) -> None:
        """
        Print a visual representation of the tree.
        
        Useful for debugging. Shows tree structure with proper indentation.
        """
        with self._lock:
            if self.root is None:
                print("(empty tree)")
                return
            self._print_tree_recursive(self.root, "", True)
    
    def _print_tree_recursive(
        self,
        node: Optional[AVLNode],
        prefix: str,
        is_last: bool
    ) -> None:
        """Recursively print tree with visual formatting."""
        if node is not None:
            print(prefix + ("└── " if is_last else "├── ") + str(node.val))
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            # Print right child first (appears on top visually).
            if node.right or node.left:
                self._print_tree_recursive(node.right, new_prefix, node.left is None)
            if node.left:
                self._print_tree_recursive(node.left, new_prefix, True)


# =============================================================================
# EXAMPLE USAGE AND TESTING
# =============================================================================

if __name__ == "__main__":
    # Configure logging for the demonstration.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("AVL Tree Production Demo")
    print("=" * 60)
    
    # Create a tree with limits.
    tree = AVLTree(max_size=100, max_depth=50, enable_logging=True)
    
    # Test insertions.
    print("\n--- Inserting values: 10, 20, 30, 40, 50, 25 ---")
    for val in [10, 20, 30, 40, 50, 25]:
        tree.insert(val)
    
    # Print tree structure.
    print("\n--- Tree Structure ---")
    tree.print_tree()
    
    # Test traversals.
    print("\n--- Traversals ---")
    print(f"In-order:   {tree.in_order_traversal()}")
    print(f"Pre-order:  {tree.pre_order_traversal()}")
    print(f"Post-order: {tree.post_order_traversal()}")
    
    # Test search.
    print("\n--- Search ---")
    print(f"Search for 25: {tree.search(25)}")
    print(f"Search for 99: {tree.search(99)}")
    
    # Test Python magic methods.
    print("\n--- Python Integration ---")
    print(f"len(tree) = {len(tree)}")
    print(f"25 in tree = {25 in tree}")
    print(f"99 in tree = {99 in tree}")
    print(f"list(tree) = {list(tree)}")
    
    # Test deletion.
    print("\n--- Deleting 20 ---")
    tree.delete(20)
    print(f"After deletion: {tree.in_order_traversal()}")
    tree.print_tree()
    
    # Test validation.
    print("\n--- Validation ---")
    print(f"Is valid AVL tree: {tree.is_valid_avl()}")
    
    # Test serialization.
    print("\n--- Serialization ---")
    data = tree.to_list()
    print(f"Exported: {data}")
    
    new_tree = AVLTree()
    new_tree.from_list(data)
    print(f"Imported: {new_tree.to_list()}")
    
    # Test min/max.
    print("\n--- Min/Max ---")
    print(f"Minimum: {tree.get_min()}")
    print(f"Maximum: {tree.get_max()}")
    
    # Test properties.
    print("\n--- Properties ---")
    print(f"Size: {tree.size}")
    print(f"Height: {tree.height}")
    print(f"Is empty: {tree.is_empty}")
    
    # Test capacity limit.
    print("\n--- Testing Capacity Limit ---")
    small_tree = AVLTree(max_size=3)
    try:
        for i in range(10):
            small_tree.insert(i)
    except AVLTreeCapacityError as e:
        print(f"Caught expected error: {e}")
    
    # Test invalid key.
    print("\n--- Testing Invalid Key ---")
    try:
        tree.insert(None)
    except AVLTreeKeyError as e:
        print(f"Caught expected error: {e}")
    
    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)
