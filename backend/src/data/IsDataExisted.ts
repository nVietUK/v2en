import {
	ValidationOptions,
	ValidatorConstraint,
	ValidatorConstraintInterface,
	registerDecorator,
} from 'class-validator';
import { hash } from 'bcrypt';
import { DataController } from './data.controller';

@ValidatorConstraint({ async: true })
export class IsDataExistedConstraint implements ValidatorConstraintInterface {
	constructor(private readonly dataService: DataController) {}
	validate(value: string) {
		return hash(value, 12).then((value) => {
			return this.dataService
				.findOneBy({ hashValue: value })
				.then((data) => {
					return !data;
				});
		});
	}
}

export function IsDataExisted(validationOptions?: ValidationOptions) {
	return function (object: any, propertyName: string) {
		registerDecorator({
			target: object.constructor,
			propertyName: propertyName,
			options: validationOptions,
			constraints: [],
			validator: IsDataExistedConstraint,
		});
	};
}
