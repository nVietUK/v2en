import { Injectable } from '@nestjs/common';
import {
	registerDecorator,
	ValidationOptions,
	ValidatorConstraint,
	ValidatorConstraintInterface,
} from 'class-validator';
import { DataService } from './data.service';

export function IsDataExistedByHashValue(validationOptions?: ValidationOptions) {
	return function (object: any, propertyName: string) {
		registerDecorator({
			name: 'isDataExisted',
			target: object.constructor,
			propertyName,
			options: validationOptions,
			validator: IsDataExistedByHashValueConstraint,
		});
	};
}

@Injectable()
@ValidatorConstraint({ async: true })
export class IsDataExistedByHashValueConstraint implements ValidatorConstraintInterface {
	constructor(private readonly connection: DataService) {}

	async validate(value: any): Promise<boolean> {
		return await this.createQueryBuilder(value);
	}

	private createQueryBuilder(value: any) {
		return !this.connection.findOneBy({ hashValue: value });
	}
}
