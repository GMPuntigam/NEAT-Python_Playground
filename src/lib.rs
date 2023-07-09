use std::fs;

use favannat::{MatrixRecurrentFabricator, StatefulFabricator, StatefulEvaluator, MatrixRecurrentEvaluator};
use set_genome::Genome;
extern crate libc;

use libc::{c_char, c_double};
use std::ffi::{CStr};

#[derive(Debug)]
pub struct NetworkEvaluator {
    evaluator: MatrixRecurrentEvaluator,
}

impl NetworkEvaluator {

    fn construct(string: *const c_char) -> NetworkEvaluator {
        let c_str = unsafe {
            assert!(!string.is_null());
    
            CStr::from_ptr(string)
        };
        let gen: Genome;
        let champion_bytes = &fs::read_to_string(format!("{}", c_str.to_str().expect("CStr::from_bytes_with_nul failed"))).expect("Unable to read champion");
        gen = serde_json::from_str(champion_bytes).unwrap();
        NetworkEvaluator{
            evaluator: MatrixRecurrentFabricator::fabricate(&gen).expect("didnt work")
        }
    }
    fn evaluate(&mut self, input_values: Vec<f64>) -> Vec<f64> {
        let eval = &mut self.evaluator;
        let result = eval.evaluate(input_values);
        result
    }
}

#[no_mangle]
pub extern "C" fn construct_network(string: *const c_char) -> *mut NetworkEvaluator {
    Box::into_raw(Box::new(NetworkEvaluator::construct(string)))
}

#[repr(C)]
pub struct NetworkPrediction {
    phi1:  c_double,
    phi2:  c_double,
    phi3:  c_double
    
}
#[derive(Debug, Clone, Copy)]
#[repr(C)]
pub struct POINT {
    x: c_double,
    y: c_double,
}

#[derive(Debug, Clone, Copy)]
#[repr(C)]
pub struct AdditionalInputs {
    step: c_double,
    bias: c_double,
    f_change:c_double
}


#[no_mangle]
pub extern "C" fn evaluate_network(p1: POINT,p2: POINT, p3: POINT, p4: POINT,additional_inputs: AdditionalInputs, ptr: *mut NetworkEvaluator) -> *const NetworkPrediction {
    let x1_float: POINT;
    let x2_float: POINT;
    let x3_float: POINT;
    let x4_float: POINT;
    x1_float = p1.clone();
    // println!("x-1 {:?}", x1_float.x);
    // println!("f-1 {:?}", x1_float.y);
    x2_float = p2.clone();
    // println!("x-2 {:?}", x2_float.x);
    // println!("f-2 {:?}", x2_float.y);
    x3_float = p3.clone();
    x4_float = p4.clone();
    // println!("x-3 {:?}", x3_float.x);
    // println!("f-3 {:?}", x3_float.y);
    let stepfloat_float = additional_inputs.clone();
    println!("{:?}", stepfloat_float);
    let evaluator = unsafe {
        assert!(!ptr.is_null());
        &mut *ptr
    };
    let vals:Vec<f64> = vec![x1_float.x, x2_float.x, x3_float.x, x4_float.x, x1_float.y, x2_float.y, x3_float.y,x4_float.y, stepfloat_float.step, stepfloat_float.bias, stepfloat_float.f_change];
    let result = evaluator.evaluate(vals);
    Box::into_raw(Box::new(NetworkPrediction{
        phi1: result[0],
        phi2: result[1],
        phi3: result[2],
    }))
}

#[no_mangle]
pub extern "C" fn terminate_evaluator(ptr: *mut NetworkEvaluator) {
    if ptr.is_null() {
        return;
    }
    unsafe {
        _ = Box::from_raw(ptr);
    }
}